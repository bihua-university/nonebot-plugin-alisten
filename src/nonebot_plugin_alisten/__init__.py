"""Alisten 插件"""

from nonebot import get_driver, logger, require
from nonebot.drivers import HTTPClientMixin
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_user")
require("nonebot_plugin_orm")

__plugin_meta__ = PluginMetadata(
    name="Alisten",
    description="通过 Alisten 服务点歌",
    usage="""参数为歌曲相关信息
/music Sagitta luminis               # 搜索并点歌（默认为网易云）
/点歌 青花瓷                          # 中文别名
/music BV1Xx411c7md                  # Bilibili BV号
/music qq:song_name                  # QQ音乐
/music wy:song_name                  # 网易云音乐

配置命令（仅限超级用户）：
/alisten config set <server_url> <house_id> [house_password]  # 设置配置
/alisten config show                                          # 查看当前配置
/alisten config delete                                        # 删除配置

支持的音乐源：
• wy: 网易云音乐（默认）
• qq: QQ音乐
• db: Bilibili""",
    type="application",
    homepage="https://github.com/bihua-university/nonebot-plugin-alisten",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna", "nonebot_plugin_user"),
)

driver = get_driver()
if isinstance(driver, HTTPClientMixin):
    from .matchers import alisten_config_cmd as alisten_config_cmd
    from .matchers import music_cmd as music_cmd
else:
    logger.warning("当前驱动器不支持 HTTP 客户端功能，插件已禁用")
