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
async def test_music_skip_success(app: App, respx_mock: respx.MockRouter):
    """测试投票切歌成功"""
    from nonebot_plugin_alisten import alisten_cmd

    skip_mock = respx_mock.post("http://localhost:8080/music/skip/vote").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"current_votes": 1, "required_votes": 2},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music skip"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="投票跳过，当前票数：1/2",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = skip_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "user": {"name": "nickname", "email": "nickname@example.com"},
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_skip_immediately(app: App, respx_mock: respx.MockRouter):
    """测试投票切歌成功并立即切歌"""
    from nonebot_plugin_alisten import alisten_cmd

    skip_mock = respx_mock.post("http://localhost:8080/music/skip/vote").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"current_votes": 1, "required_votes": 1},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music skip"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="投票跳过，当前票数：1/1",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = skip_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {"houseId": "room123", "password": "password123", "user": {"name": "nickname", "email": "nickname@example.com"}}
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_skip_failure(app: App, respx_mock: respx.MockRouter):
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
        {"houseId": "room123", "password": "password123", "user": {"name": "nickname", "email": "nickname@example.com"}}
    )
