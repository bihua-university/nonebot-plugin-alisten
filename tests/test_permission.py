from inline_snapshot import snapshot
from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App

from tests.fake import fake_group_message_event_v11, fake_private_message_event_v11


async def test_private(app: App):
    """测试私聊场景"""

    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_private_message_event_v11(message=Message("/alisten"))
        ctx.receive_event(bot, event)
        ctx.should_not_pass_rule(alisten_cmd)


async def test_config_permission_denied(app: App):
    """测试非超级用户无法使用配置命令"""
    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(
            message=Message("/alisten config delete"),
            user_id=10000,  # 普通用户
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "权限不足，仅限超级用户使用")
        ctx.should_finished(alisten_cmd)


async def test_shortcut(app: App):
    """测试设置快捷指令"""

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_private_message_event_v11(message=Message("/alisten --shortcut list"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            snapshot("""\
[/]music ...args
[/]点歌 ...args
[/]搜索音乐 ...args
[/]当前音乐 ...args
[/]切歌 ...args
[/]播放列表 ...args
[/]点赞音乐 ...args
[/]删除音乐 ...args
[/]播放模式 ...args\
"""),
        )
        ctx.should_finished()


async def test_shortcut_permission_denied(app: App):
    """测试设置快捷指令权限不足"""

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_private_message_event_v11(message=Message("/alisten --shortcut list"), user_id=10000)
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "参数 --shortcut 匹配失败")
        ctx.should_finished()
