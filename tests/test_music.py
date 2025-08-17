import json

import httpx
import pytest
import respx
from inline_snapshot import snapshot
from nonebot import get_adapter, get_driver
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message, MessageSegment
from nonebug import App

from tests.fake import fake_group_message_event_v11, fake_private_message_event_v11


async def test_music_no_config(app: App):
    """测试没有配置的情况"""
    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/music test"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message="当前群组未配置 Alisten 服务\n请联系管理员使用 /alisten config set 命令进行配置",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_success(app: App, respx_mock: respx.MockRouter):
    """测试音乐点歌成功"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "message": "点歌成功",
                "data": {
                    "name": "测试歌曲",
                    "source": "wy",
                    "id": "123456",
                },
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/music test"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="点歌成功！歌曲已加入播放列表\n歌曲：测试歌曲\n来源：网易云音乐",
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


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_by_id(app: App, respx_mock: respx.MockRouter):
    """测试音乐点歌成功"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "message": "点歌成功",
                "data": {
                    "name": "测试歌曲",
                    "source": "wy",
                    "id": "123456",
                },
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/music --id 123456"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="点歌成功！歌曲已加入播放列表\n歌曲：测试歌曲\n来源：网易云音乐",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "housePwd": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
            "id": "123456",
            "name": "",
            "source": "wy",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_failure(app: App, respx_mock: respx.MockRouter):
    """测试音乐点歌失败"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=400,
            json={
                "error": "点歌失败，无法获取音乐信息",
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/music test"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="点歌失败，无法获取音乐信息", at_sender=True)
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


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_bilibili(app: App, respx_mock: respx.MockRouter):
    """测试 Bilibili BV 号点歌"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "message": "点歌成功",
                "data": {
                    "name": "【测试】Bilibili视频",
                    "source": "db",
                    "id": "BV1Xx411c7md",
                },
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/music BV1Xx411c7md"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message="点歌成功！歌曲已加入播放列表\n歌曲：【测试】Bilibili视频\n来源：Bilibili",
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
            "name": "BV1Xx411c7md",
            "source": "db",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_get_arg(app: App, respx_mock: respx.MockRouter):
    """测试交互式点歌"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "message": "点歌成功",
                "data": {
                    "name": "测试歌曲",
                    "source": "wy",
                    "id": "123456",
                },
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        # 不提供歌曲名，应该询问
        event = fake_group_message_event_v11(message=Message("/music"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "你想听哪首歌呢？")
        ctx.should_rejected(alisten_cmd)

        # 提供无效输入（图片），应该重新询问
        event = fake_group_message_event_v11(message=Message(MessageSegment.image("12")))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "你想听哪首歌呢？")
        ctx.should_rejected(alisten_cmd)

        # 提供有效歌曲名
        event = fake_group_message_event_v11(message=Message("test"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "点歌成功！歌曲已加入播放列表\n歌曲：测试歌曲\n来源：网易云音乐", at_sender=True)
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


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_qq(app: App, respx_mock: respx.MockRouter):
    """测试 QQ 音乐点歌"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "message": "点歌成功",
                "data": {
                    "name": "青花瓷",
                    "source": "qq",
                    "id": "123456",
                },
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/music qq:青花瓷"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="点歌成功！歌曲已加入播放列表\n歌曲：青花瓷\n来源：QQ音乐",
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
            "name": "青花瓷",
            "source": "qq",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_success_no_email(app: App, respx_mock: respx.MockRouter):
    """测试音乐点歌，没有邮箱的情况"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "message": "点歌成功",
                "data": {
                    "name": "测试歌曲",
                    "source": "wy",
                    "id": "123456",
                },
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/music test"), user_id=10000)
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="点歌成功！歌曲已加入播放列表\n歌曲：测试歌曲\n来源：网易云音乐",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "housePwd": "password123",
            "user": {"name": "nickname10000", "email": ""},
            "id": "",
            "name": "test",
            "source": "wy",
        }
    )


async def test_music_private(app: App):
    """测试私聊场景"""
    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_private_message_event_v11(message=Message("/music test"))
        ctx.receive_event(bot, event)
        ctx.should_not_pass_rule(alisten_cmd)


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_api_response_content_none(app: App, respx_mock: respx.MockRouter):
    """通过 matcher 发送 /music，当后端返回空 content 时，应由 matcher 返回通用错误信息"""
    from nonebot_plugin_alisten import alisten_cmd

    # 模拟后端返回空 content
    respx_mock.post("http://localhost:8080/music/pick").mock(return_value=httpx.Response(status_code=200, content=None))

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/music test"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="响应内容为空，请稍后重试", at_sender=True)
        ctx.should_finished(alisten_cmd)


@pytest.mark.usefixtures("_configs")
async def test_music_api_request_exception(app: App, monkeypatch: pytest.MonkeyPatch):
    """当 driver.request 抛异常时，通过 matcher 点歌应返回通用错误信息"""
    from nonebot_plugin_alisten import alisten_cmd

    # patch driver.request 抛异常
    driver = get_driver()

    async def fake_request(_):
        raise RuntimeError("network error")

    monkeypatch.setattr(driver, "request", fake_request)

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/music test"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="点歌请求失败，请稍后重试", at_sender=True)
        ctx.should_finished(alisten_cmd)


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_playlist_success(app: App, respx_mock: respx.MockRouter):
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
async def test_playlist_empty(app: App, respx_mock: respx.MockRouter):
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
async def test_playlist_failure(app: App, respx_mock: respx.MockRouter):
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


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_delete_music_success(app: App, respx_mock: respx.MockRouter):
    """测试删除音乐成功"""
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
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})
    last_request = delete_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "housePwd": "password123",
            "id": "s2",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_delete_music_not_found(app: App, respx_mock: respx.MockRouter):
    """测试删除音乐时未找到指定音乐"""
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
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_delete_music_failure(app: App, respx_mock: respx.MockRouter):
    """测试删除音乐失败"""
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
    assert json.loads(last_request.content) == snapshot({"houseId": "room123", "housePwd": "password123"})
    last_request = delete_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "housePwd": "password123",
            "id": "s2",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_good_music_success(app: App, respx_mock: respx.MockRouter):
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
        {"houseId": "room123", "housePwd": "password123", "index": 1, "name": ""}
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_good_music_not_found(app: App, respx_mock: respx.MockRouter):
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
async def test_good_music_failure(app: App, respx_mock: respx.MockRouter):
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
        {"houseId": "room123", "housePwd": "password123", "index": 1, "name": ""}
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_vote_skip_success(app: App, respx_mock: respx.MockRouter):
    """测试投票切歌成功"""
    from nonebot_plugin_alisten import alisten_cmd

    skip_mock = respx_mock.post("http://localhost:8080/music/skip/vote").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"code": "20000", "message": "投票成功", "current_votes": 1},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music skip"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="投票成功，当前票数：1/3",
            at_sender=True,
        )
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
async def test_vote_skip_immediately(app: App, respx_mock: respx.MockRouter):
    """测试投票切歌成功并立即切歌"""
    from nonebot_plugin_alisten import alisten_cmd

    skip_mock = respx_mock.post("http://localhost:8080/music/skip/vote").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"code": "20000", "message": "投票成功，歌曲已跳过"},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music skip"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="投票成功，歌曲已跳过",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = skip_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {"houseId": "room123", "housePwd": "password123", "user": {"name": "nickname", "email": "nickname@example.com"}}
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_vote_skip_failure(app: App, respx_mock: respx.MockRouter):
    """测试投票切歌失败"""
    from nonebot_plugin_alisten import alisten_cmd

    skip_mock = respx_mock.post("http://localhost:8080/music/skip/vote").mock(
        return_value=httpx.Response(
            status_code=400,
            json={"error": "投票失败"},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music skip"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="投票失败",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = skip_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {"houseId": "room123", "housePwd": "password123", "user": {"name": "nickname", "email": "nickname@example.com"}}
    )


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
