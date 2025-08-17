import json

import httpx
import pytest
import respx
from inline_snapshot import snapshot
from nonebot import get_adapter, get_driver
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App

from tests.fake import fake_group_message_event_v11


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_info(app: App, respx_mock: respx.MockRouter):
    """测试房间信息"""
    from nonebot_plugin_alisten import alisten_cmd

    respx_mock.get("http://localhost:8080/house/search").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "data": [
                    {
                        "createTime": 1755320090631,
                        "desc": "BHU 听歌房",
                        "enableStatus": True,
                        "id": "room123",
                        "name": "BHU 听歌房",
                        "needPwd": True,
                        "population": 0,
                    }
                ],
                "message": "房间列表",
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten house info"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "当前房间信息:\n房间ID: room123\n房间名称: BHU 听歌房\n房间描述: BHU 听歌房\n当前人数: 0",
        )
        ctx.should_finished(alisten_cmd)


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_empty(app: App, respx_mock: respx.MockRouter):
    """测试房间列表为空"""
    from nonebot_plugin_alisten import alisten_cmd

    respx_mock.get("http://localhost:8080/house/search").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "data": [],
                "message": "房间列表",
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten house info"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "未找到任何房间")
        ctx.should_finished(alisten_cmd)


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_info_not_exist(app: App, respx_mock: respx.MockRouter):
    """测试房间信息"""
    from nonebot_plugin_alisten import alisten_cmd

    respx_mock.get("http://localhost:8080/house/search").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "data": [
                    {
                        "createTime": 1755320090631,
                        "desc": "BHU 听歌房",
                        "enableStatus": True,
                        "id": "room_not_exist",
                        "name": "BHU 听歌房",
                        "needPwd": True,
                        "population": 0,
                    }
                ],
                "message": "房间列表",
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten house info"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "未找到房间ID为 room123 的房间")
        ctx.should_finished(alisten_cmd)


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_search_response_content_none(app: App, respx_mock: respx.MockRouter):
    """通过 /alisten house info 测试当后端返回空 content 时的异常处理"""
    from nonebot_plugin_alisten import alisten_cmd

    respx_mock.get("http://localhost:8080/house/search").mock(
        return_value=httpx.Response(status_code=200, content=None)
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten house info"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="响应内容为空，请稍后重试")
        ctx.should_finished(alisten_cmd)


@pytest.mark.usefixtures("_configs")
async def test_house_search_request_exception(app: App, monkeypatch: pytest.MonkeyPatch):
    """当 driver.request 抛异常时，通过 matcher 查询房间信息应返回通用错误信息"""
    from nonebot_plugin_alisten import alisten_cmd

    # patch driver.request 抛异常
    driver = get_driver()

    async def fake_request(_):
        raise RuntimeError("network error")

    monkeypatch.setattr(driver, "request", fake_request)

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten house info"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="房间搜索请求失败，请稍后重试")
        ctx.should_finished(alisten_cmd)


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_user(app: App, respx_mock: respx.MockRouter):
    """测试获取房间用户列表"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.get("http://localhost:8080/house/houseuser").mock(
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
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_user_empty(app: App, respx_mock: respx.MockRouter):
    """测试获取空的房间用户列表"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.get("http://localhost:8080/house/houseuser").mock(
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
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_user_failure(app: App, respx_mock: respx.MockRouter):
    """测试获取房间用户列表失败"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.get("http://localhost:8080/house/houseuser").mock(
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
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})
