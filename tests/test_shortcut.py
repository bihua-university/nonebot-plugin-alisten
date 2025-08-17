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
async def test_shortcut_playlist(app: App, respx_mock: respx.MockRouter):
    """测试快捷命令 "播放列表" """
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.get("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(status_code=200, json={"playlist": []})
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/播放列表"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="播放列表为空", at_sender=True)
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_delete_music(app: App, respx_mock: respx.MockRouter):
    """测试快捷命令 "删除音乐" """
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.get("http://localhost:8080/music/playlist").mock(
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
        return_value=httpx.Response(status_code=200, json={"code": "20000", "message": "删除成功"})
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/删除音乐 Song to Delete"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="删除成功", at_sender=True)
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})
    last_request = delete_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123", "id": "s2"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_good_music(app: App, respx_mock: respx.MockRouter):
    """测试快捷命令 "点赞" """
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
        return_value=httpx.Response(status_code=200, json={"code": "20000", "message": "点赞成功", "likes": 1})
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/点赞 Song to Like"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="点赞成功，当前点赞数：1", at_sender=True)
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})
    last_request = good_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {"houseId": "room123", "housePwd": "password123", "index": 1, "name": ""}
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_skip_music(app: App, respx_mock: respx.MockRouter):
    """测试快捷命令 "切歌" """
    from nonebot_plugin_alisten import alisten_cmd

    skip_mock = respx_mock.post("http://localhost:8080/music/skip/vote").mock(
        return_value=httpx.Response(status_code=200, json={"code": "20000", "message": "投票成功", "current_votes": 1})
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/切歌"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="投票成功，当前票数：1/3", at_sender=True)
        ctx.should_finished(alisten_cmd)

    last_request = skip_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "housePwd": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_pick_music(app: App, respx_mock: respx.MockRouter):
    """测试快捷命令 "点歌" """
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "message": "点歌成功",
                "data": {"name": "测试歌曲", "source": "wy", "id": "123456"},
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/点歌 test"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message=("点歌成功！歌曲已加入播放列表\n歌曲：测试歌曲\n来源：网易云音乐"),
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "housePwd": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
            "id": "",
            "name": "test",
            "source": "wy",
        }
    )
