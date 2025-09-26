import json

import httpx
import pytest
import respx
from inline_snapshot import snapshot
from nonebot import get_adapter, get_driver
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message, MessageSegment
from nonebot.adapters.onebot.v11.event import Reply, Sender
from nonebug import App

from tests.fake import fake_group_message_event_v11, fake_private_message_event_v11


async def test_music_pick_pick_no_config(app: App):
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
async def test_music_pick_success(app: App, respx_mock: respx.MockRouter):
    """测试音乐点歌成功"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "name": "测试歌曲",
                "source": "wy",
                "id": "123456",
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
            "password": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
            "id": "",
            "name": "test",
            "source": "wy",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_pick_by_id(app: App, respx_mock: respx.MockRouter):
    """测试音乐点歌成功"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "name": "测试歌曲",
                "source": "wy",
                "id": "123456",
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
            "password": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
            "id": "123456",
            "name": "",
            "source": "wy",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_pick_failure(app: App, respx_mock: respx.MockRouter):
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
            "password": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
            "id": "",
            "name": "test",
            "source": "wy",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_pick_bilibili(app: App, respx_mock: respx.MockRouter):
    """测试 Bilibili BV 号点歌"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "name": "【测试】Bilibili视频",
                "source": "db",
                "id": "BV1Xx411c7md",
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
            "password": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
            "id": "",
            "name": "BV1Xx411c7md",
            "source": "db",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_pick_get_arg(app: App, respx_mock: respx.MockRouter):
    """测试交互式点歌"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "name": "测试歌曲",
                "source": "wy",
                "id": "123456",
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
            "password": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
            "id": "",
            "name": "test",
            "source": "wy",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_pick_qq(app: App, respx_mock: respx.MockRouter):
    """测试 QQ 音乐点歌"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "name": "青花瓷",
                "source": "qq",
                "id": "123456",
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
            "password": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
            "id": "",
            "name": "青花瓷",
            "source": "qq",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_pick_url_common(app: App, respx_mock: respx.MockRouter):
    """测试通用链接点歌"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "name": "ノウワンライト feat.可不・初音ミク / 歌蝕",
                "source": "url_common",
                "id": "https://www.youtube.com/watch?v=QxeR9NiDEsc",
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(
            message=Message("/链接点歌 听网址 https://www.youtube.com/watch?v=QxeR9NiDEsc")
        )
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="点歌成功！歌曲已加入播放列表\n歌曲：ノウワンライト feat.可不・初音ミク / 歌蝕\n来源：通用链接",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
            "id": "https://www.youtube.com/watch?v=QxeR9NiDEsc",
            "name": "",
            "source": "url_common",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_pick_url_common_invalid(app: App, respx_mock: respx.MockRouter):
    """测试通用链接点歌，无效链接"""
    from nonebot_plugin_alisten import alisten_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/链接点歌 没有网址"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(event=event, message="无效的链接格式，请重新尝试", at_sender=True)
        ctx.should_finished(alisten_cmd)


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_pick_any_source(app: App, respx_mock: respx.MockRouter):
    """测试任意源点歌"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "name": "青花瓷",
                "source": "any",
                "id": "123456",
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/music any:青花瓷"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="点歌成功！歌曲已加入播放列表\n歌曲：青花瓷\n来源：any",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
            "id": "",
            "name": "青花瓷",
            "source": "any",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_pick_success_no_email(app: App, respx_mock: respx.MockRouter):
    """测试音乐点歌，没有邮箱的情况"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "name": "测试歌曲",
                "source": "wy",
                "id": "123456",
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
            "password": "password123",
            "user": {"name": "nickname10000", "email": ""},
            "id": "",
            "name": "test",
            "source": "wy",
        }
    )


async def test_music_pick_private(app: App):
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
async def test_music_pick_api_response_content_none(app: App, respx_mock: respx.MockRouter):
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
async def test_music_pick_api_request_exception(app: App, monkeypatch: pytest.MonkeyPatch):
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
async def test_music_pick_reply_message(app: App, respx_mock: respx.MockRouter):
    """测试回复消息点歌"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/pick").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "name": "测试歌曲",
                "source": "wy",
                "id": "123456",
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        # 构造一个回复消息，内容为 "青花瓷"
        reply = Reply(
            time=1234567890,
            message_id=12345,
            message=Message("青花瓷"),
            message_type="group",
            real_id=12345,
            sender=Sender(),
        )

        event = fake_group_message_event_v11(message=Message("/点歌"), reply=reply)
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
            "password": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
            "id": "",
            "name": "青花瓷",
            "source": "wy",
        }
    )
