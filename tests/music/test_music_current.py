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
async def test_music_current_success(app: App, respx_mock: respx.MockRouter):
    """测试获取当前音乐成功"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/sync").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "data": {
                    "name": "测试歌曲",
                    "source": "wy",
                    "id": "123456",
                    "user": {"name": "test_user", "email": "test@example.com"},
                }
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music current"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message="当前播放：测试歌曲\n来源：网易云音乐\n点歌者：test_user",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_current_no_music(app: App, respx_mock: respx.MockRouter):
    """测试当前没有播放音乐"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/sync").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"data": None},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music current"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="当前没有播放音乐", at_sender=True)
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_current_failure(app: App, respx_mock: respx.MockRouter):
    """测试获取当前音乐失败"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/sync").mock(
        return_value=httpx.Response(
            status_code=400,
            json={"error": "获取当前音乐失败"},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music current"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="获取当前音乐失败", at_sender=True)
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})
