import pytest
from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App

from tests.fake import fake_group_message_event_v11


@pytest.mark.usefixtures("_configs")
async def test_config_delete_with_config(app: App):
    """测试删除配置（有配置时）"""
    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(
            message=Message("/alisten config delete"),
            sender_id=10,  # 超级用户
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "Alisten 配置已删除")
        ctx.should_finished(alisten_cmd)

        # 检查是否删除成功
        event = fake_group_message_event_v11(
            message=Message("/alisten config show"),
            sender_id=10,  # 超级用户
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "当前群组未配置 Alisten 服务")
        ctx.should_finished(alisten_cmd)


async def test_config_delete_no_config(app: App):
    """测试删除配置（无配置时）"""
    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(
            message=Message("/alisten config delete"),
            sender_id=10,  # 超级用户
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "当前群组未配置 Alisten 服务")
        ctx.should_finished(alisten_cmd)
