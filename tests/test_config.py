import pytest
from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App

from tests.fake import fake_group_message_event_v11, fake_private_message_event_v11


async def test_config_set_new(app: App):
    """测试设置新配置"""
    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(
            message=Message("/alisten config set http://example.com room123 pass123"),
            sender_id=10,  # 超级用户
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "Alisten 配置已设置:\n服务器地址: http://example.com\n房间ID: room123\n房间密码: 已设置",
        )
        ctx.should_finished(alisten_cmd)

        # 检查是否设置成功
        event = fake_group_message_event_v11(
            message=Message("/alisten config show"),
            sender_id=10,  # 超级用户
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "当前 Alisten 配置:\n服务器地址: http://example.com\n房间ID: room123\n房间密码: 已设置",
        )
        ctx.should_finished(alisten_cmd)


@pytest.mark.usefixtures("_configs")
async def test_config_set_update_existing(app: App):
    """测试更新现有配置"""
    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(
            message=Message("/alisten config set http://newserver.com newroom"),
            sender_id=10,  # 超级用户
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "Alisten 配置已设置:\n服务器地址: http://newserver.com\n房间ID: newroom\n房间密码: 未设置",
        )
        ctx.should_finished(alisten_cmd)

        # 检查是否更新成功
        event = fake_group_message_event_v11(
            message=Message("/alisten config show"),
            sender_id=10,  # 超级用户
        )
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "当前 Alisten 配置:\n服务器地址: http://newserver.com\n房间ID: newroom\n房间密码: 未设置",
        )
        ctx.should_finished(alisten_cmd)


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


async def test_config_private(app: App):
    """测试私聊场景"""
    from nonebot.adapters.onebot.v11 import Message

    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_private_message_event_v11(message=Message("/alisten"))
        ctx.receive_event(bot, event)
        ctx.should_not_pass_rule(alisten_cmd)
