"""常量定义，用于存放插件内共享的字面量和映射。"""

from enum import StrEnum


class PlayMode(StrEnum):
    SEQUENTIAL = "sequential"
    RANDOM = "random"


# 默认音乐来源
DEFAULT_SOURCE = "wy"


# 全称映射（用于对用户展示）
SOURCE_NAMES_FULL: dict[str, str] = {
    "wy": "网易云音乐",
    "qq": "QQ音乐",
    "db": "Bilibili",
    "url_common": "通用链接",
}

# 简称映射（短展示）
SOURCE_NAMES_SHORT: dict[str, str] = {
    "wy": "网易云",
    "qq": "QQ音乐",
    "db": "B站",
    "url_common": "通用",
}
