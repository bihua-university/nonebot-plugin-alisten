from arclet.alconna import AllParam
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.permission import SuperUser
from nonebot.rule import Rule
from nonebot_plugin_alconna import (
    Alconna,
    AlconnaQuery,
    Args,
    Check,
    CommandMeta,
    Match,
    Option,
    Query,
    Subcommand,
    UniMessage,
    match_path,
    on_alconna,
    store_true,
)
from nonebot_plugin_orm import async_scoped_session
from nonebot_plugin_user import UserSession

from .alisten_api import (
    AlistenAPI,
    ErrorResponse,
    PickMusicResponse,
)
from .depends import get_alisten_api, get_config
from .models import AlistenConfig


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
            Subcommand("delete", Args["name#要删除的音乐名称", AllParam], help_text="从播放列表中删除指定音乐"),
            Subcommand("good", Args["name#要点赞的音乐名称", AllParam], help_text="为播放列表中的音乐点赞"),
            Subcommand("skip", help_text="发起投票跳过当前音乐"),
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
/alisten music playlist                         # 查看播放列表
/alisten music delete 青花瓷                    # 从播放列表删除音乐
/alisten music good 青花瓷                      # 为音乐点赞
/alisten music skip                             # 发起投票跳过当前音乐

/alisten house info                             # 查看房间信息
/alisten house user                             # 查看房间用户列表

/alisten config set http://localhost:8080 room123 password123  # 设置或更新配置
/alisten config set https://music.example.com myroom          # 设置配置（无密码）
/alisten config show                                           # 查看当前配置
/alisten config delete                                         # 删除配置""",
        ),
    ),
    use_cmd_start=True,
    block=True,
    rule=Rule(is_group),
)
alisten_cmd.shortcut("music", {"command": "alisten music pick", "prefix": True})
alisten_cmd.shortcut("点歌", {"command": "alisten music pick", "prefix": True})
alisten_cmd.shortcut("播放列表", {"command": "alisten music playlist", "prefix": True})
alisten_cmd.shortcut("点赞", {"command": "alisten music good", "prefix": True})
alisten_cmd.shortcut("切歌", {"command": "alisten music skip", "prefix": True})
alisten_cmd.shortcut("删除音乐", {"command": "alisten music delete", "prefix": True})


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

    source = "wy"  # 默认音乐源

    # 解析特殊格式的输入
    if ":" in keywords_str:
        # 格式如 "wy:song_name" 或 "qq:song_name"
        parts = keywords_str.split(":", 1)
        if len(parts) == 2 and parts[0] in ["wy", "qq", "db"]:
            source = parts[0]
            keywords_str = parts[1]
    elif keywords_str.startswith("BV"):
        # Bilibili BV号
        source = "db"

    if id.result:
        result = await api.pick_music(id=keywords_str, name="", source=source)
    else:
        result = await api.pick_music(id="", name=keywords_str, source=source)

    if isinstance(result, PickMusicResponse):
        msg = "点歌成功！歌曲已加入播放列表"
        msg += f"\n歌曲：{result.data.name}"
        source_name = {
            "wy": "网易云音乐",
            "qq": "QQ音乐",
            "db": "Bilibili",
        }.get(result.data.source, result.data.source)
        msg += f"\n来源：{source_name}"
        await alisten_cmd.finish(msg, at_sender=True)
    else:
        await alisten_cmd.finish(result.error, at_sender=True)


@alisten_cmd.assign("config.set", parameterless=[Depends(ensure_superuser)])
async def handle_config_set(
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
async def handle_config_show(config: AlistenConfig | None = Depends(get_config)):
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
async def handle_config_delete(
    db_session: async_scoped_session,
    config: AlistenConfig | None = Depends(get_config),
):
    """删除配置"""
    if not config:
        await alisten_cmd.finish("当前群组未配置 Alisten 服务")

    await db_session.delete(config)
    await db_session.commit()

    await alisten_cmd.finish("Alisten 配置已删除")


@alisten_cmd.assign("music.playlist")
async def playlist_handle(
    api: AlistenAPI = Depends(get_alisten_api),
):
    """获取播放列表"""
    result = await api.get_playlist()

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)

    if not result.playlist:
        await alisten_cmd.finish("播放列表为空", at_sender=True)

    msg = "当前播放列表：\n"
    for i, item in enumerate(result.playlist, 1):
        source_name = {
            "wy": "网易云",
            "qq": "QQ音乐",
            "db": "B站",
        }.get(item.source, item.source)

        msg += f"{i}. {item.name} [{source_name}]"
        if item.likes > 0:
            msg += f" ❤️{item.likes}"
        msg += f" - {item.user.name}\n"

    await alisten_cmd.finish(msg.strip(), at_sender=True)


@alisten_cmd.assign("music.delete")
async def delete_music_handle(
    name: UniMessage,
    api: AlistenAPI = Depends(get_alisten_api),
):
    """删除音乐"""
    playlist_result = await api.get_playlist()
    if isinstance(playlist_result, ErrorResponse):
        await alisten_cmd.finish(playlist_result.error, at_sender=True)

    if not playlist_result.playlist:
        await alisten_cmd.finish("播放列表为空", at_sender=True)

    for item in playlist_result.playlist[1:]:
        if item.name == name.extract_plain_text().strip():
            music_id = item.id
            break
    else:
        await alisten_cmd.finish("未找到指定音乐", at_sender=True)

    result = await api.delete_music(music_id)

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)

    await alisten_cmd.finish(result.message, at_sender=True)


@alisten_cmd.assign("music.good")
async def good_music_handle(
    name: UniMessage,
    api: AlistenAPI = Depends(get_alisten_api),
):
    """点赞音乐"""
    playlist_result = await api.get_playlist()
    if isinstance(playlist_result, ErrorResponse):
        await alisten_cmd.finish(playlist_result.error, at_sender=True)

    if not playlist_result.playlist:
        await alisten_cmd.finish("播放列表为空", at_sender=True)

    for i, item in enumerate(playlist_result.playlist, 1):
        if item.name == name.extract_plain_text().strip():
            index = i
            break
    else:
        await alisten_cmd.finish("未找到指定音乐", at_sender=True)

    result = await api.good_music(index)

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)

    await alisten_cmd.finish(f"{result.message}，当前点赞数：{result.likes}", at_sender=True)


@alisten_cmd.assign("music.skip")
async def vote_skip_handle(
    api: AlistenAPI = Depends(get_alisten_api),
):
    """投票跳过"""
    result = await api.vote_skip()

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)
    elif result.current_votes is not None:
        await alisten_cmd.finish(f"{result.message}，当前票数：{result.current_votes}/3", at_sender=True)
    else:
        await alisten_cmd.finish(result.message, at_sender=True)


@alisten_cmd.assign("house.info")
async def handle_house_info(
    api: AlistenAPI = Depends(get_alisten_api),
):
    """获取当前房间的信息"""
    result = await api.house_info()
    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error)

    await alisten_cmd.finish(
        f"当前房间信息:\n"
        f"房间ID: {result.id}\n"
        f"房间名称: {result.name}\n"
        f"房间描述: {result.desc}\n"
        f"当前人数: {result.population}"
    )


@alisten_cmd.assign("house.user")
async def house_user_handle(
    api: AlistenAPI = Depends(get_alisten_api),
):
    """获取房间用户列表"""
    result = await api.get_house_user()

    if isinstance(result, ErrorResponse):
        await alisten_cmd.finish(result.error, at_sender=True)

    if not result.data:
        await alisten_cmd.finish("房间内暂无用户", at_sender=True)

    msg = f"房间用户列表（共 {len(result.data)} 人）：\n"
    for i, user in enumerate(result.data, 1):
        msg += f"{i}. {user.name}"
        msg += "\n"

    await alisten_cmd.finish(msg.strip(), at_sender=True)
