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
