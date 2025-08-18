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
async def test_music_good_success(app: App, respx_mock: respx.MockRouter):
    """测试点赞音乐成功"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.get("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "playlist": [
                    {
                        "id": "s1",
                        "name": "Song to Like",
                        "source": "wy",
                        "user": {"name": "user1", "email": ""},
                        "likes": 0,
                    },
                    {
                        "id": "s2",
                        "name": "Another Song",
                        "source": "qq",
                        "user": {"name": "user2", "email": ""},
                        "likes": 0,
                    },
                ]
            },
        )
    )
    good_mock = respx_mock.post("http://localhost:8080/music/good").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"code": "20000", "message": "点赞成功", "likes": 1},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music good Song to Like"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="点赞成功，当前点赞数：1",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})
    last_request = good_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {"houseId": "room123", "housePwd": "password123", "index": 1, "name": "Song to Like"}
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_good_not_found(app: App, respx_mock: respx.MockRouter):
    """测试点赞音乐时未找到指定音乐"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.get("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "playlist": [
                    {"id": "s1", "name": "A Song", "source": "wy", "user": {"name": "user1", "email": ""}, "likes": 0},
                ]
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music good NonExistent Song"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="未找到指定音乐",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_good_failure(app: App, respx_mock: respx.MockRouter):
    """测试点赞音乐失败"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.get("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "playlist": [
                    {
                        "id": "s1",
                        "name": "Song to Like",
                        "source": "wy",
                        "user": {"name": "user1", "email": ""},
                        "likes": 0,
                    },
                ]
            },
        )
    )
    good_mock = respx_mock.post("http://localhost:8080/music/good").mock(
        return_value=httpx.Response(
            status_code=400,
            json={"error": "点赞失败"},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music good Song to Like"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="点赞失败",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})
    last_request = good_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {"houseId": "room123", "housePwd": "password123", "index": 1, "name": "Song to Like"}
    )
