from arclet.alconna import AllParam, config
from nonebot import get_driver, logger
from nonebot.adapters import MessageTemplate
from nonebot.matcher import Matcher
from nonebot.params import Arg, Depends
from nonebot.permission import SuperUser
from nonebot.rule import Rule
from nonebot.typing import T_State
from nonebot_plugin_alconna import (
    Alconna,
    AlconnaQuery,
    Args,
    Check,
    CommandMeta,
    Match,
    Namespace,
    Option,
    Query,
    Subcommand,
    UniMessage,
    command_manager,
    match_path,
    on_alconna,
    store_true,
)
from nonebot_plugin_alconna.builtins.extensions.reply import ReplyMergeExtension
from nonebot_plugin_localstore import get_plugin_cache_dir
from nonebot_plugin_orm import async_scoped_session
from nonebot_plugin_user import UserSession

from .alisten_api import (
    AlistenAPI,
    ErrorResponse,
    PickMusicResponse,
    PlaylistItem,
)
from .constants import (
    DEFAULT_SOURCE,
    SOURCE_NAMES_FULL,
    SOURCE_NAMES_SHORT,
    PlayMode,
)
from .depends import get_alisten_api, get_config
from .extensions import SuperUserShortcutExtension
from .models import AlistenConfig

ns = Namespace("alisten", disable_builtin_options=set())
config.namespaces["alisten"] = ns

driver = get_driver()
cache_dir = get_plugin_cache_dir() / "shortcut.db"


@driver.on_startup
async def _() -> None:
    command_manager.load_cache(cache_dir)
    logger.debug("快捷指令缓存加载完成")


@driver.on_shutdown
async def _() -> None:
    command_manager.dump_cache(cache_dir)
    logger.debug("快捷指令缓存已保存")


async def is_group(user_session: UserSession) -> bool:
    """确保在群组中使用"""
    return not user_session.session.scene.is_private


async def ensure_superuser(matcher: Matcher, is_superuser: bool = Depends(SuperUser())):
    """确保是超级用户"""
    if not is_superuser:
        await matcher.finish("权限不足，仅限超级用户使用")


alisten_cmd = on_alconna(
    Alconna(
        "alisten",
        Subcommand(
            "music",
            Subcommand(
                "pick",
                Option("--id", default=False, action=store_true, help_text="使用音乐ID点歌"),
                Args["keywords?#音乐名称或信息", AllParam],
                help_text=("点歌：按名称、BV号或指定平台搜索并点歌"),
            ),
            Subcommand("playlist", help_text="查看当前房间播放列表"),
            Subcommand("delete", Args["name?#要删除的音乐名称", AllParam], help_text="从播放列表中删除指定音乐"),
            Subcommand("good", Args["name?#要点赞的音乐名称", AllParam], help_text="为播放列表中的音乐点赞"),
            Subcommand("skip", help_text="发起投票跳过当前音乐"),
            Subcommand("search", Args["keywords#搜索关键词", AllParam], help_text="搜索音乐"),
            Subcommand("current", help_text="查看当前播放的音乐"),
            Subcommand("playmode", Args["mode#播放模式", str], help_text="设置播放模式(顺序播放/随机播放)"),
            help_text="音乐管理",
        ),
        Subcommand(
            "config",
            Subcommand(
                "set",
                Args["server_url", str]["house_id", str]["house_password?", str],
                help_text="设置服务器配置，包括服务器地址、房间ID和可选的房间密码",
            ),
            Subcommand("show", help_text="显示当前群组的配置"),
            Subcommand("delete", help_text="删除当前群组的配置"),
            help_text="管理服务器配置",
        ),
        Subcommand(
            "house",
            Subcommand("info", help_text="显示当前房间的信息"),
            Subcommand("user", help_text="显示当前房间的用户列表"),
            help_text="管理房间",
        ),
        meta=CommandMeta(
            description="听歌房管理",
            example="""/alisten music pick 青花瓷                 # 点歌并加入播放列表
/alisten music pick --id 30621776               # 通过 ID 点歌
/alisten music search 青花瓷                    # 搜索音乐
/alisten music current                          # 查看当前播放的音乐
/alisten music playlist                         # 查看播放列表
/alisten music delete 青花瓷                    # 从播放列表删除音乐
/alisten music good 青花瓷                      # 为音乐点赞
/alisten music skip                             # 发起投票跳过当前音乐
/alisten music playmode 顺序播放                  # 设置为顺序播放模式
/alisten music playmode 随机播放                  # 设置为随机播放模式

/alisten house info                             # 查看房间信息
/alisten house user                             # 查看房间用户列表

/alisten config set http://localhost:8080 room123 password123  # 设置或更新配置
/alisten config set https://music.example.com myroom          # 设置配置（无密码）
/alisten config show                                           # 查看当前配置
/alisten config delete                                         # 删除配置""",
        ),
        namespace=config.namespaces["alisten"],
    ),
    use_cmd_start=True,
    block=True,
    rule=Rule(is_group),
    skip_for_unmatch=False,
    extensions=[SuperUserShortcutExtension(), ReplyMergeExtension()],
)
alisten_cmd.shortcut("music", {"command": "alisten music pick", "prefix": True})
alisten_cmd.shortcut("点歌", {"command": "alisten music pick", "prefix": True})
alisten_cmd.shortcut("搜索音乐", {"command": "alisten music search", "prefix": True})
alisten_cmd.shortcut("当前音乐", {"command": "alisten music current", "prefix": True})
alisten_cmd.shortcut("切歌", {"command": "alisten music skip", "prefix": True})
alisten_cmd.shortcut("播放列表", {"command": "alisten music playlist", "prefix": True})
alisten_cmd.shortcut("点赞音乐", {"command": "alisten music good", "prefix": True})
alisten_cmd.shortcut("删除音乐", {"command": "alisten music delete", "prefix": True})
alisten_cmd.shortcut("播放模式", {"command": "alisten music playmode", "prefix": True})


@alisten_cmd.assign("music.pick")
async def music_pick_handle_first_receive(
    keywords: Match[UniMessage],
    config: AlistenConfig | None = Depends(get_config),
):
    # 首先检查是否有配置
    if not config:
        await alisten_cmd.finish(
            "当前群组未配置 Alisten 服务\n请联系管理员使用 /alisten config set 命令进行配置",
            at_sender=True,
        )

    if keywords.available:
        alisten_cmd.set_path_arg("music.pick.keywords", keywords.result)


@alisten_cmd.got_path("music.pick.keywords", prompt="你想听哪首歌呢？", parameterless=[Check(match_path("music.pick"))])
async def music_pick_handle(
    keywords: UniMessage,
    id: Query[bool] = AlconnaQuery("music.pick.id.value", False),
    api: AlistenAPI = Depends(get_alisten_api),
):
    """处理点歌请求"""
    keywords_str = keywords.extract_plain_text().strip()
    if not keywords_str:
        await alisten_cmd.reject_path("music.pick.keywords", "你想听哪首歌呢？")

    source = DEFAULT_SOURCE  # 默认音乐源

    # 解析特殊格式的输入
    if ":" in keywords_str:
        # 格式如 "wy:song_name" 或 "qq:song_name"
        parts = keywords_str.split(":", 1)
        if len(parts) == 2:
            source = parts[0]
            keywords_str = parts[1]
    # Bilibili BV号
    elif keywords_str.startswith("BV"):
        source = "db"

    if id.result:
        result = await api.music_pick(id=keywords_str, name="", source=source)
    else:
        result = await api.music_pick(id="", name=keywords_str, source=source)

    if isinstance(result, PickMusicResponse):
        msg = "点歌成功！歌曲已加入播放列表"
        msg += f"\n歌曲：{result.name}"
        source_name = SOURCE_NAMES_FULL.get(result.source, result.source)
        msg += f"\n来源：{source_name}"
        await alisten_cmd.finish(msg, at_sender=True)
    else:
        await alisten_cmd.finish(result.error, at_sender=True)


@alisten_cmd.assign("music.playlist")
async def music_playlist_handle(
    api: AlistenAPI = Depends(get_alisten_api),
):
    """获取播放列表"""
    result = await api.music_playlist()

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)

    if not result.playlist:
        await alisten_cmd.finish("播放列表为空", at_sender=True)

    msg = "当前播放列表：\n"
    for i, item in enumerate(result.playlist, 1):
        source_name = SOURCE_NAMES_SHORT.get(item.source, item.source)

        msg += f"{i}. {item.name} [{source_name}]"
        if item.likes > 0:
            msg += f" ❤️{item.likes}"
        msg += f" - {item.user.name}\n"

    await alisten_cmd.finish(msg.strip(), at_sender=True)


@alisten_cmd.assign("music.delete")
async def music_delete_handle_first_receive(
    name: Match[UniMessage],
    state: T_State,
    api: AlistenAPI = Depends(get_alisten_api),
):
    if name.available:
        alisten_cmd.set_path_arg("music.delete.name", name.result)
        state["playlist"] = None
    else:
        playlist = await api.music_playlist()
        if isinstance(playlist, ErrorResponse):
            await alisten_cmd.finish(playlist.error, at_sender=True)

        if not playlist.playlist:
            await alisten_cmd.finish("当前播放列表为空", at_sender=True)

        state["playlist"] = playlist.playlist
        state["playlist_prompt"] = "\n".join(f"{index}. {item.name}" for index, item in enumerate(playlist.playlist, 1))


@alisten_cmd.got_path(
    "music.delete.name",
    prompt=MessageTemplate("你想删除哪首歌呢？\n\n{playlist_prompt}"),
    parameterless=[Check(match_path("music.delete"))],
)
async def music_delete_handle(
    name: UniMessage,
    playlist: list[PlaylistItem] | None = Arg(),
    api: AlistenAPI = Depends(get_alisten_api),
):
    """删除音乐"""
    name_str = name.extract_plain_text().strip()
    if playlist is None:
        request_name = name_str
    elif name_str.isdigit() and len(name_str) <= 2:
        for index, item in enumerate(playlist, 1):
            if str(index) == name_str:
                request_name = item.name
                break
        else:
            await alisten_cmd.finish("无效的序号，请重新尝试", at_sender=True)
    else:
        request_name = name_str

    result = await api.music_delete(id=request_name)

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)

    await alisten_cmd.finish(f"已删除音乐：{result.name}", at_sender=True)


@alisten_cmd.assign("music.good")
async def music_good_handle_first_receive(
    name: Match[UniMessage],
    state: T_State,
    api: AlistenAPI = Depends(get_alisten_api),
):
    playlist = await api.music_playlist()
    if isinstance(playlist, ErrorResponse):
        await alisten_cmd.finish(playlist.error, at_sender=True)

    if not playlist.playlist:
        await alisten_cmd.finish("当前播放列表为空", at_sender=True)

    state["playlist"] = playlist.playlist

    if name.available:
        alisten_cmd.set_path_arg("music.good.name", name.result)
    else:
        state["playlist_prompt"] = "\n".join(f"{index}. {item.name}" for index, item in enumerate(playlist.playlist, 1))


@alisten_cmd.got_path(
    "music.good.name",
    prompt=MessageTemplate("你想为哪首歌点赞呢？\n\n{playlist_prompt}"),
    parameterless=[Check(match_path("music.good"))],
)
async def music_good_handle(
    name: UniMessage,
    playlist: list[PlaylistItem] = Arg(),
    api: AlistenAPI = Depends(get_alisten_api),
):
    """点赞音乐"""
    name_str = name.extract_plain_text().strip()

    request_index = None
    request_name = None

    if name_str.isdigit() and len(name_str) <= 2:
        if int(name_str) > len(playlist) or int(name_str) < 1:
            await alisten_cmd.finish("无效的序号，请重新尝试", at_sender=True)
        request_index = int(name_str)
        request_name = playlist[request_index - 1].name
    else:
        for index, item in enumerate(playlist, 1):
            if item.name == name_str:
                request_index = index
                request_name = item.name
                break
        else:
            await alisten_cmd.finish("无效的歌曲名称，请重新尝试", at_sender=True)

    result = await api.music_good(request_index, request_name)

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)

    await alisten_cmd.finish(f"点赞成功：{result.name}，当前点赞数：{result.likes}", at_sender=True)


@alisten_cmd.assign("music.skip")
async def music_skip_handle(
    api: AlistenAPI = Depends(get_alisten_api),
):
    """投票跳过"""
    result = await api.music_skip_vote()

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)
    else:
        required_str = f"/{result.required_votes}" if result.required_votes else ""
        await alisten_cmd.finish(f"投票跳过，当前票数：{result.current_votes}{required_str}", at_sender=True)


@alisten_cmd.assign("music.search")
async def music_search_handle(
    keywords: UniMessage,
    api: AlistenAPI = Depends(get_alisten_api),
):
    """搜索音乐"""
    keywords_str = keywords.extract_plain_text().strip()

    source = DEFAULT_SOURCE  # 默认音乐源

    # 解析特殊格式的输入
    if ":" in keywords_str:
        # 格式如 "wy:song_name" 或 "qq:song_name"
        parts = keywords_str.split(":", 1)
        if len(parts) == 2:
            source = parts[0]
            keywords_str = parts[1]

    result = await api.music_search(name=keywords_str, source=source)

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)

    if not result.data:
        await alisten_cmd.finish("未找到相关音乐", at_sender=True)

    msg = f"搜索结果（关键词：{keywords_str}）：\n"
    source_name = SOURCE_NAMES_FULL.get(source, source)
    msg += f"来源：{source_name}\n\n"

    for i, item in enumerate(result.data, 1):  # 只显示前10个结果
        msg += f"{i}. {item.name} - {item.artist} (ID: {item.id})\n"

    msg += "\n使用 /alisten music pick --id <ID> 来点歌"
    await alisten_cmd.finish(msg.strip(), at_sender=True)


@alisten_cmd.assign("music.current")
async def music_current_handle(
    api: AlistenAPI = Depends(get_alisten_api),
):
    """查看当前播放的音乐"""
    result = await api.music_sync()

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)

    source_name = SOURCE_NAMES_FULL.get(result.source or "", result.source or "")

    msg = f"当前播放：{result.name}\n"
    msg += f"来源：{source_name}\n"
    if result.user:
        msg += f"点歌者：{result.user.name}\n"

    await alisten_cmd.finish(msg.strip(), at_sender=True)


@alisten_cmd.assign("music.playmode")
async def music_playmode_handle(
    mode: str,
    api: AlistenAPI = Depends(get_alisten_api),
):
    """设置播放模式"""
    # 将中文模式转换为对应参数
    mode_mapping = {
        "顺序播放": PlayMode.SEQUENTIAL,
        "随机播放": PlayMode.RANDOM,
        "sequential": PlayMode.SEQUENTIAL,
        "random": PlayMode.RANDOM,
    }

    if mode not in mode_mapping:
        await alisten_cmd.finish("播放模式只能是 '顺序播放' 或 '随机播放'", at_sender=True)

    mode_value = mode_mapping[mode]
    result = await api.music_playmode(mode_value)

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)

    mode_name = "顺序播放" if mode_value == PlayMode.SEQUENTIAL else "随机播放"
    await alisten_cmd.finish(f"播放模式已设置为：{mode_name}", at_sender=True)


@alisten_cmd.assign("config.set", parameterless=[Depends(ensure_superuser)])
async def config_set_handle(
    user_session: UserSession,
    db_session: async_scoped_session,
    server_url: str,
    house_id: str,
    house_password: str = "",
    existing_config: AlistenConfig | None = Depends(get_config),
):
    """设置 Alisten 配置"""
    if existing_config:
        # 更新现有配置
        existing_config.server_url = server_url
        existing_config.house_id = house_id
        existing_config.house_password = house_password
    else:
        # 创建新配置
        new_config = AlistenConfig(
            session_id=user_session.session_id,
            server_url=server_url,
            house_id=house_id,
            house_password=house_password,
        )
        db_session.add(new_config)

    await db_session.commit()

    await alisten_cmd.finish(
        f"Alisten 配置已设置:\n"
        f"服务器地址: {server_url}\n"
        f"房间ID: {house_id}\n"
        f"房间密码: {'已设置' if house_password else '未设置'}"
    )


@alisten_cmd.assign("config.show", parameterless=[Depends(ensure_superuser)])
async def config_show_handle(config: AlistenConfig | None = Depends(get_config)):
    """显示当前配置"""
    if not config:
        await alisten_cmd.finish("当前群组未配置 Alisten 服务")

    await alisten_cmd.finish(
        f"当前 Alisten 配置:\n"
        f"服务器地址: {config.server_url}\n"
        f"房间ID: {config.house_id}\n"
        f"房间密码: {'已设置' if config.house_password else '未设置'}"
    )


@alisten_cmd.assign("config.delete", parameterless=[Depends(ensure_superuser)])
async def config_delete_handle(
    db_session: async_scoped_session,
    config: AlistenConfig | None = Depends(get_config),
):
    """删除配置"""
    if not config:
        await alisten_cmd.finish("当前群组未配置 Alisten 服务")

    await db_session.delete(config)
    await db_session.commit()

    await alisten_cmd.finish("Alisten 配置已删除")


@alisten_cmd.assign("house.info")
async def house_info_handle(
    api: AlistenAPI = Depends(get_alisten_api),
):
    """获取当前房间的信息"""
    result = await api.house_search()
    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error)

    # 检查房间列表是否为空
    if not result:
        await alisten_cmd.finish("未找到任何房间")

    # 在房间列表中查找匹配的房间
    for house in result:
        if house.id == api.config.house_id:
            await alisten_cmd.finish(
                f"当前房间信息:\n"
                f"房间ID: {house.id}\n"
                f"房间名称: {house.name}\n"
                f"房间描述: {house.desc}\n"
                f"当前人数: {house.population}"
            )

    await alisten_cmd.finish(f"未找到房间ID为 {api.config.house_id} 的房间")


@alisten_cmd.assign("house.user")
async def house_user_handle(
    api: AlistenAPI = Depends(get_alisten_api),
):
    """获取房间用户列表"""
    result = await api.house_houseuser()

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)

    if not result:
        await alisten_cmd.finish("房间内暂无用户", at_sender=True)

    msg = f"房间用户列表（共 {len(result)} 人）：\n"
    for i, user in enumerate(result, 1):
        msg += f"{i}. {user.name}"
        msg += "\n"

    await alisten_cmd.finish(msg.strip(), at_sender=True)
