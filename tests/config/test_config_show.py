import pytest
from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App

from tests.fake import fake_group_message_event_v11


@pytest.mark.usefixtures("_configs")
async def test_config_show_with_config(app: App):
    """测试显示配置（有配置时）"""
    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten config show"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "当前 Alisten 配置:\n服务器地址: http://localhost:8080\n房间ID: room123\n房间密码: 已设置",
        )
        ctx.should_finished(alisten_cmd)


async def test_config_show_no_config(app: App):
    """测试显示配置（无配置时）"""
    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten config show"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "当前群组未配置 Alisten 服务")
        ctx.should_finished(alisten_cmd)
