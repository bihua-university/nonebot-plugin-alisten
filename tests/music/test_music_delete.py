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
async def test_music_delete_success(app: App, respx_mock: respx.MockRouter):
    """测试删除音乐成功"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.post("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "playlist": [
                    {
                        "id": "s1",
                        "name": "Current Song",
                        "source": "wy",
                        "user": {"name": "user1", "email": ""},
                        "likes": 0,
                    },
                    {
                        "id": "s2",
                        "name": "Song to Delete",
                        "source": "qq",
                        "user": {"name": "user2", "email": ""},
                        "likes": 0,
                    },
                ]
            },
        )
    )
    delete_mock = respx_mock.post("http://localhost:8080/music/delete").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"code": "20000", "message": "删除成功"},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music delete Song to Delete"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="删除成功",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})
    last_request = delete_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "id": "s2",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_delete_not_found(app: App, respx_mock: respx.MockRouter):
    """测试删除音乐时未找到指定音乐"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.post("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "playlist": [
                    {
                        "id": "s1",
                        "name": "Current Song",
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

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music delete NonExistent Song"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="未找到指定音乐",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_delete_failure(app: App, respx_mock: respx.MockRouter):
    """测试删除音乐失败"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.post("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "playlist": [
                    {
                        "id": "s1",
                        "name": "Current Song",
                        "source": "wy",
                        "user": {"name": "user1", "email": ""},
                        "likes": 0,
                    },
                    {
                        "id": "s2",
                        "name": "Song to Delete",
                        "source": "qq",
                        "user": {"name": "user2", "email": ""},
                        "likes": 0,
                    },
                ]
            },
        )
    )
    delete_mock = respx_mock.post("http://localhost:8080/music/delete").mock(
        return_value=httpx.Response(
            status_code=400,
            json={"error": "删除失败"},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music delete Song to Delete"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="删除失败",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})
    last_request = delete_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "id": "s2",
        }
    )
