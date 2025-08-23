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
async def test_music_search_success(app: App, respx_mock: respx.MockRouter):
    """测试搜索音乐成功"""
    from nonebot_plugin_alisten import alisten_cmd

    search_mock = respx_mock.post("http://localhost:8080/music/search").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "list": [
                    {
                        "id": "123456",
                        "name": "青花瓷",
                        "artist": "周杰伦",
                    },
                    {
                        "id": "789012",
                        "name": "青花瓷 (钢琴版)",
                        "artist": "Various Artists",
                    },
                ],
                "totalSize": 2,
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music search 青花瓷"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message=(
                "搜索结果（关键词：青花瓷）：\n来源：网易云音乐\n\n"
                "1. 青花瓷 - 周杰伦 (ID: 123456)\n"
                "2. 青花瓷 (钢琴版) - Various Artists (ID: 789012)\n\n"
                "使用 /alisten music pick --id <ID> 来点歌"
            ),
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = search_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "name": "青花瓷",
            "source": "wy",
            "pageSize": 10,
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_search_with_source_prefix(app: App, respx_mock: respx.MockRouter):
    """测试搜索音乐带音源前缀"""
    from nonebot_plugin_alisten import alisten_cmd

    search_mock = respx_mock.post("http://localhost:8080/music/search").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "list": [
                    {
                        "id": "qq123456",
                        "name": "稻香",
                        "artist": "周杰伦",
                    },
                ],
                "totalSize": 1,
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music search qq:稻香"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message=(
                "搜索结果（关键词：稻香）：\n来源：QQ音乐\n\n"
                "1. 稻香 - 周杰伦 (ID: qq123456)\n\n"
                "使用 /alisten music pick --id <ID> 来点歌"
            ),
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = search_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "name": "稻香",
            "source": "qq",
            "pageSize": 10,
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_search_no_results(app: App, respx_mock: respx.MockRouter):
    """测试搜索音乐无结果"""
    from nonebot_plugin_alisten import alisten_cmd

    search_mock = respx_mock.post("http://localhost:8080/music/search").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "list": [],
                "totalSize": 0,
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music search 不存在的歌曲"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="未找到相关音乐",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = search_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "name": "不存在的歌曲",
            "source": "wy",
            "pageSize": 10,
        }
    )


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_search_api_error(app: App, respx_mock: respx.MockRouter):
    """测试搜索音乐API错误"""
    from nonebot_plugin_alisten import alisten_cmd

    search_mock = respx_mock.post("http://localhost:8080/music/search").mock(
        return_value=httpx.Response(
            status_code=400,
            json={"error": "搜索服务暂时不可用"},
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music search 青花瓷"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message="搜索服务暂时不可用",
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = search_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "name": "青花瓷",
            "source": "wy",
            "pageSize": 10,
        }
    )


@pytest.mark.usefixtures("_configs")
async def test_music_search_empty_keywords(app: App):
    """测试搜索音乐空关键词"""

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten music search"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(event=event, message="参数 keywords 丢失")
        ctx.should_finished()


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_music_search_invalid_source_prefix(app: App, respx_mock: respx.MockRouter):
    """测试搜索音乐无效音源前缀"""
    from nonebot_plugin_alisten import alisten_cmd

    search_mock = respx_mock.post("http://localhost:8080/music/search").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "list": [
                    {
                        "id": "123456",
                        "name": "invalid:test",
                        "artist": "测试艺术家",
                    },
                ],
                "totalSize": 1,
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        # 无效的音源前缀应该作为普通关键词处理
        event = fake_group_message_event_v11(message=Message("/alisten music search invalid:test"))
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event=event,
            message=(
                "搜索结果（关键词：invalid:test）：\n来源：网易云音乐\n\n"
                "1. invalid:test - 测试艺术家 (ID: 123456)\n\n"
                "使用 /alisten music pick --id <ID> 来点歌"
            ),
            at_sender=True,
        )
        ctx.should_finished(alisten_cmd)

    last_request = search_mock.calls.last.request
    assert json.loads(last_request.content) == snapshot(
        {
            "houseId": "room123",
            "password": "password123",
            "name": "invalid:test",
            "source": "wy",
            "pageSize": 10,
        }
    )
