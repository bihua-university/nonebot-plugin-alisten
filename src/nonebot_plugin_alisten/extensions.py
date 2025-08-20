from arclet.alconna import Alconna
from nonebot.internal.adapter import Bot, Event
from nonebot.permission import SuperUser
from nonebot_plugin_alconna import Extension, UniMessage


class SuperUserShortcutExtension(Extension):
    """用于设置仅超级用户可使用内置选项 --shortcut 的扩展"""

    @property
    def priority(self) -> int:
        return 20

    @property
    def id(self) -> str:
        return "nonebot_plugin_alisten.extensions:SuperUserShortcutExtension"

    async def receive_wrapper(self, bot: Bot, event: Event, command: Alconna, receive: UniMessage) -> UniMessage:
        if await SuperUser()(bot, event):
            command.namespace_config.disable_builtin_options.discard("shortcut")
        else:
            command.namespace_config.disable_builtin_options.add("shortcut")
        return receive
