"""Alisten 服务器 API 客户端"""

from typing import cast

from nonebot import get_driver
from nonebot.drivers import HTTPClientMixin, Request
from nonebot.log import logger
from nonebot_plugin_user import UserSession
from pydantic import BaseModel

from .models import AlistenConfig


class User(BaseModel):
    name: str
    email: str


class PickMusicRequest(BaseModel):
    """点歌请求"""

    houseId: str
    housePwd: str = ""
    user: User
    id: str = ""
    name: str = ""
    source: str = "wy"


class MusicData(BaseModel):
    """音乐数据"""

    name: str
    source: str
    id: str


class SuccessResponse(BaseModel):
    """成功响应"""

    code: str
    message: str
    data: MusicData


class ErrorResponse(BaseModel):
    """错误响应"""

    error: str


class AlistenAPI:
    """Alisten API 客户端"""

    def __init__(self, config: AlistenConfig, session: UserSession):
        self.config = config
        self.session = session

    async def pick_music(self, name: str, source: str) -> SuccessResponse | ErrorResponse:
        """点歌

        Args:
            name: 音乐名称或搜索关键词
            user_name: 用户昵称
            source: 音乐源 (wy/qq/db)
            config: Alisten 配置

        Returns:
            点歌结果
        """
        request_data = PickMusicRequest(
            houseId=self.config.house_id,
            housePwd=self.config.house_password,
            user=User(name=self.session.user_name, email=self.session.user_email or ""),
            name=name,
            source=source,
        )

        url = f"{self.config.server_url}/music/pick"

        try:
            driver = cast("HTTPClientMixin", get_driver())

            # 创建请求对象
            request = Request(
                method="POST",
                url=url,
                headers={"Content-Type": "application/json"},
                json=request_data.model_dump(),
            )

            response = await driver.request(request)
            if response.content is None:
                return ErrorResponse(error="响应内容为空")

            if response.status_code == 200:
                success_response = SuccessResponse.model_validate_json(response.content)
                return success_response

            else:
                error_response = ErrorResponse.model_validate_json(response.content)
                return error_response

        except Exception:
            logger.exception("Alisten API 请求失败")
            return ErrorResponse(error="请求失败，请稍后重试")
