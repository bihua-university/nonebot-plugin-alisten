from nonebot.params import Depends
from nonebot_plugin_orm import async_scoped_session
from nonebot_plugin_user import UserSession
from sqlalchemy import select

from .alisten_api import AlistenAPI
from .models import AlistenConfig


async def get_config(user: UserSession, db_session: async_scoped_session) -> AlistenConfig | None:
    """获取 Alisten 配置"""
    stmt = select(AlistenConfig).where(AlistenConfig.session_id == user.session_id)
    result = await db_session.execute(stmt)
    return result.scalar_one_or_none()


async def get_alisten_api(
    session: UserSession,
    config: AlistenConfig | None = Depends(get_config),
) -> AlistenAPI | None:
    """获取 Alisten API 实例"""
    if config:
        return AlistenAPI(config=config, session=session)

    return None
