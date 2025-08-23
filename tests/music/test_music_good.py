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

    playlist_mock = respx_mock.post("http://localhost:8080/music/playlist").mock(
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
            json={"name": "Song to Like", "likes": 1},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music good Song to Like"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="点赞成功：Song to Like，当前点赞数：1",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})
    last_request = good_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {"houseId": "room123", "password": "password123", "index": 1, "name": "Song to Like"}
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_good_interactive_by_name(app: App, respx_mock: respx.MockRouter):
    """测试交互式点赞音乐（通过歌曲名）"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.post("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "playlist": [
                    {
                        "id": "s1",
                        "name": "测试歌曲1",
                        "source": "wy",
                        "user": {"name": "user1", "email": ""},
                        "likes": 0,
                    },
                    {
                        "id": "s2",
                        "name": "测试歌曲2",
                        "source": "qq",
                        "user": {"name": "user2", "email": ""},
                        "likes": 1,
                    },
                ]
            },
        )
    )
    good_mock = respx_mock.post("http://localhost:8080/music/good").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"name": "测试歌曲1", "likes": 1},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        # 不提供歌曲名，应该显示播放列表并询问
        event = fake_group_message_event_v11(message=Message("/alisten music good"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "你想为哪首歌点赞呢？\n\n1. 测试歌曲1\n2. 测试歌曲2",
        )
        ctx.should_rejected(alisten_cmd)

        # 提供歌曲名称
        event = fake_group_message_event_v11(message=Message("测试歌曲1"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message="点赞成功：测试歌曲1，当前点赞数：1",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})
    last_request = good_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {"houseId": "room123", "password": "password123", "index": 1, "name": "测试歌曲1"}
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_good_interactive_by_number(app: App, respx_mock: respx.MockRouter):
    """测试交互式点赞音乐（通过序号）"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.post("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "playlist": [
                    {
                        "id": "s1",
                        "name": "测试歌曲1",
                        "source": "wy",
                        "user": {"name": "user1", "email": ""},
                        "likes": 0,
                    },
                    {
                        "id": "s2",
                        "name": "测试歌曲2",
                        "source": "qq",
                        "user": {"name": "user2", "email": ""},
                        "likes": 1,
                    },
                ]
            },
        )
    )
    good_mock = respx_mock.post("http://localhost:8080/music/good").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"name": "测试歌曲2", "likes": 2},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        # 不提供歌曲名，应该显示播放列表并询问
        event = fake_group_message_event_v11(message=Message("/alisten music good"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "你想为哪首歌点赞呢？\n\n1. 测试歌曲1\n2. 测试歌曲2",
        )
        ctx.should_rejected(alisten_cmd)

        # 提供序号
        event = fake_group_message_event_v11(message=Message("2"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message="点赞成功：测试歌曲2，当前点赞数：2",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})
    last_request = good_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {"houseId": "room123", "password": "password123", "index": 2, "name": "测试歌曲2"}
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_good_interactive_invalid_number(app: App, respx_mock: respx.MockRouter):
    """测试交互式点赞音乐（无效序号）"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.post("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "playlist": [
                    {
                        "id": "s1",
                        "name": "测试歌曲1",
                        "source": "wy",
                        "user": {"name": "user1", "email": ""},
                        "likes": 0,
                    },
                ]
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        # 不提供歌曲名，应该显示播放列表并询问
        event = fake_group_message_event_v11(message=Message("/alisten music good"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "你想为哪首歌点赞呢？\n\n1. 测试歌曲1",
        )
        ctx.should_rejected(alisten_cmd)

        # 提供无效序号
        event = fake_group_message_event_v11(message=Message("3"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message="无效的序号，请重新尝试",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_good_interactive_empty_playlist(app: App, respx_mock: respx.MockRouter):
    """测试交互式点赞音乐（播放列表为空）"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.post("http://localhost:8080/music/playlist").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"playlist": []},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        # 不提供歌曲名，播放列表为空时应该直接结束
        event = fake_group_message_event_v11(message=Message("/alisten music good"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message="当前播放列表为空",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_good_not_found(app: App, respx_mock: respx.MockRouter):
    """测试点赞音乐时未找到指定音乐"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.post("http://localhost:8080/music/playlist").mock(
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
            message="无效的歌曲名称，请重新尝试",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = playlist_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_good_failure(app: App, respx_mock: respx.MockRouter):
    """测试点赞音乐失败"""
    from nonebot_plugin_alisten import alisten_cmd

    playlist_mock = respx_mock.post("http://localhost:8080/music/playlist").mock(
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
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "password": "password123"})
    last_request = good_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {"houseId": "room123", "password": "password123", "index": 1, "name": "Song to Like"}
    )
