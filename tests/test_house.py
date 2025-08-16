import httpx
import pytest
import respx
from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App

from tests.fake import fake_group_message_event_v11


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_info(app: App, respx_mock: respx.MockRouter):
    """测试房间信息"""
    from nonebot_plugin_alisten import alisten_config_cmd

    respx_mock.get("http://localhost:8080/house/search").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "data": [
                    {
                        "createTime": 1755320090631,
                        "desc": "BHU 听歌房",
                        "enableStatus": True,
                        "id": "room123",
                        "name": "BHU 听歌房",
                        "needPwd": True,
                        "population": 0,
                    }
                ],
                "message": "房间列表",
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten house info"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "当前房间信息:\n房间ID: room123\n房间名称: BHU 听歌房\n房间描述: BHU 听歌房\n当前人数: 0",
        )
        ctx.should_finished(alisten_config_cmd)


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_house_info_not_exist(app: App, respx_mock: respx.MockRouter):
    """测试房间信息"""
    from nonebot_plugin_alisten import alisten_config_cmd

    respx_mock.get("http://localhost:8080/house/search").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "20000",
                "data": [
                    {
                        "createTime": 1755320090631,
                        "desc": "BHU 听歌房",
                        "enableStatus": True,
                        "id": "room_not_exist",
                        "name": "BHU 听歌房",
                        "needPwd": True,
                        "population": 0,
                    }
                ],
                "message": "房间列表",
            },
        )
    )

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/alisten house info"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "未找到房间ID为 room123 的房间")
        ctx.should_finished(alisten_config_cmd)
