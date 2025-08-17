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
async def test_music_playlist_success(app: App, respx_mock: respx.MockRouter):
    """测试获取播放列表成功"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.get("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "playlist": [
                    {
                        "id": "123",
                        "name": "Song 1",
                        "source": "wy",
                        "user": {"name": "user1", "email": "a@a.com"},
                        "likes": 5,
                    },
                    {
                        "id": "456",
                        "name": "Song 2",
                        "source": "qq",
                        "user": {"name": "user2", "email": "b@b.com"},
                        "likes": 0,
                    },
                ]
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music playlist"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="当前播放列表：\n1. Song 1 [网易云] ❤️5 - user1\n2. Song 2 [QQ音乐] - user2",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_playlist_empty(app: App, respx_mock: respx.MockRouter):
    """测试获取空的播放列表"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.get("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"playlist": []},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music playlist"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="播放列表为空",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_playlist_failure(app: App, respx_mock: respx.MockRouter):
    """测试获取播放列表失败"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.get("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=400,
            json={"error": "获取播放列表失败"},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music playlist"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="获取播放列表失败", at_sender=True)
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})
