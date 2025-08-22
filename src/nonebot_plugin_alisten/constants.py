"""常量定义，用于存放插件内共享的字面量和映射。"""

from enum import StrEnum


class Source(StrEnum):
    WY = "wy"
    QQ = "qq"
    DB = "db"


# 默认音乐来源
DEFAULT_SOURCE = Source.WY


# 全称映射（用于对用户展示）
SOURCE_NAMES_FULL: dict[str, str] = {
    Source.WY: "网易云音乐",
    Source.QQ: "QQ音乐",
    Source.DB: "Bilibili",
}

# 简称映射（短展示）
SOURCE_NAMES_SHORT: dict[str, str] = {
    Source.WY: "网易云",
    Source.QQ: "QQ音乐",
    Source.DB: "B站",
}
