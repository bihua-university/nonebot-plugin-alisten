import pytest
import respx
from inline_snapshot import snapshot
from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App

from tests.fake import fake_group_message_event_v11


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_music_playlist(app: App):
    """测试快捷命令 "播放列表" """

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/播放列表 -h"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message=snapshot("""\
/alisten music playlist \n\
查看当前房间播放列表\
"""),
        )
        ctx.should_finished()


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_music_delete(app: App):
    """测试快捷命令 "删除音乐" """

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/删除音乐 -h"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message=snapshot("""\
/alisten music delete <...name> \n\
## 注释
  name: 要删除的音乐名称
从播放列表中删除指定音乐\
"""),
        )
        ctx.should_finished()


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_music_good(app: App):
    """测试快捷命令 "点赞" """

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/点赞音乐 -h"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message=snapshot("""\
/alisten music good <...name> \n\
## 注释
  name: 要点赞的音乐名称
为播放列表中的音乐点赞\
"""),
        )
        ctx.should_finished()


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_music_skip(app: App, respx_mock: respx.MockRouter):
    """测试快捷命令 "切歌" """

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/切歌 -h"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message=snapshot("""\
/alisten music skip \n\
发起投票跳过当前音乐\
"""),
        )
        ctx.should_finished()


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_music_pick(app: App):
    """测试快捷命令 "点歌" """

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/点歌 -h"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message=snapshot("""\
/alisten music pick <...keywords> \n\
## 注释
  keywords: 音乐名称或信息
点歌：按名称、BV号或指定平台搜索并点歌

可用的选项有:
* 使用音乐ID点歌
  --id \n\
"""),
        )
        ctx.should_finished()


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_music(app: App):
    """测试快捷命令 "music" """

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/music -h"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message=snapshot("""\
/alisten music pick <...keywords> \n\
## 注释
  keywords: 音乐名称或信息
点歌：按名称、BV号或指定平台搜索并点歌

可用的选项有:
* 使用音乐ID点歌
  --id \n\
"""),
        )
        ctx.should_finished()


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_music_search(app: App):
    """测试快捷命令 "搜索音乐" """

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/搜索音乐 -h"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message=snapshot("""\
/alisten music search <...keywords> \n\
## 注释
  keywords: 搜索关键词
搜索音乐\
"""),
        )
        ctx.should_finished()


@pytest.mark.usefixtures("_configs")
@respx.mock(assert_all_called=True)
async def test_shortcut_music_current(app: App):
    """测试快捷命令 "当前音乐" """

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/当前音乐 -h"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event=event,
            message=snapshot("""\
/alisten music current \n\
查看当前播放的音乐\
"""),
        )
        ctx.should_finished()
