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
async def test_music_playmode_success(app: App, respx_mock: respx.MockRouter):
    """测试设置播放模式成功"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/playmode").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "mode": "random",
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music playmode random"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="播放模式已设置为：随机播放", at_sender=True)
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "mode": "random",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_playmode_failure(app: App, respx_mock: respx.MockRouter):
    """测试设置播放模式失败"""
    from nonebot_plugin_alisten import alisten_cmd

    mocked_api = respx_mock.post("http://localhost:8080/music/playmode").mock(
        return_value=httpx.Response(
            status_code=400,
            json={
                "error": "设置播放模式失败",
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music playmode sequential"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="设置播放模式失败", at_sender=True)
        ctx.should_finished(alisten_cmd)

    last_request = mocked_api.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "mode": "sequential",
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_playmode_invalid_mode(app: App, respx_mock: respx.MockRouter):
    """测试设置播放模式时输入无效模式"""
    from nonebot_plugin_alisten import alisten_cmd

    # 不需要模拟 API 调用，因为输入无效时不会发送请求

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music playmode invalid"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event=event, message="播放模式只能是 '顺序播放' 或 '随机播放'", at_sender=True)
        ctx.should_finished(alisten_cmd)
