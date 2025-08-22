import json

import httpx
import pytest
import respx
from inline_snapshot import snapshot
from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App

from tests.fake import fake_group_message_event_v11


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_user(app: App, respx_mock: respx.MockRouter):
    """测试获取房间用户列表"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/house/houseuser").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "data": [
                    {"name": "user1", "email": "user1@example.com"},
                    {"name": "user2", "email": ""},
                ],
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten house user"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message="房间用户列表（共 2 人）：\n1. user1\n2. user2",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_user_empty(app: App, respx_mock: respx.MockRouter):
    """测试获取空的房间用户列表"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/house/houseuser").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"code": "20000", "message": "用户列表", "data": []},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten house user"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="房间内暂无用户",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_user_failure(app: App, respx_mock: respx.MockRouter):
    """测试获取房间用户列表失败"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/house/houseuser").mock(
        return_value=httpx.Response(
            status_code=400,
            json={"error": "获取用户列表失败"},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten house user"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="获取用户列表失败", at_sender=True)
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})
