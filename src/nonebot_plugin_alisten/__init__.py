"""Alisten 插件"""

from nonebot import get_driver, logger
from nonebot.drivers import HTTPClientMixin

driver = get_driver()
if isinstance(driver, HTTPClientMixin):
    from .matchers import alisten_config_cmd as alisten_config_cmd
    from .matchers import music_cmd as music_cmd
else:
    logger.warning("当前驱动器不支持 HTTP 客户端功能，插件已禁用")
