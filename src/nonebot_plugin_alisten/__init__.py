"""Alisten 插件"""

from nonebot import get_driver, logger, require
from nonebot.drivers import HTTPClientMixin
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_user")
require("nonebot_plugin_orm")

__plugin_meta__ = PluginMetadata(
    name="Alisten",
    description="NoneBot 听歌房插件",
    usage="""
基础点歌命令：
/music Sagitta luminis      # 按歌曲名搜索并点歌（默认 wy）
/点歌 青花瓷                 # 中文别名，与 /music 等价
/music BV1Xx411c7md         # 使用 B 站 BV 号点歌
/music qq:<音乐名称>         # 指定 QQ 音乐
/music wy:<音乐名称>         # 指定网易云音乐
/music --id <平台>:<音乐ID>  # 通过 ID 点歌

音乐管理命令：
/搜索音乐 <关键词>            # 搜索音乐但不自动加入播放列表
/当前音乐                    # 查看当前正在播放的音乐信息
/切歌                       # 投票跳过当前音乐
/播放列表                    # 查看播放列表
/删除音乐 <音乐名称>          # 删除指定音乐
/点赞音乐 <音乐名称>          # 为音乐点赞
/播放模式 <模式>              # 设置播放模式（顺序播放/随机播放）

房间管理：
/alisten house info          # 查看房间信息
/alisten house user          # 查看房间用户列表

配置命令（仅限超级用户）：
/alisten config set <server_url> <house_id> [house_password]  # 设置或更新配置
/alisten config show        # 查看当前配置
/alisten config delete      # 删除当前配置

支持的音乐源：
• wy: 网易云音乐（默认）
• qq: QQ音乐
• db: Bilibili
""",
    type="application",
    homepage="https://github.com/bihua-university/nonebot-plugin-alisten",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna", "nonebot_plugin_user"),
)

driver = get_driver()
if isinstance(driver, HTTPClientMixin):
    from .matchers import alisten_cmd as alisten_cmd
else:
    logger.warning("当前驱动器不支持 HTTP 客户端功能，插件已禁用")
