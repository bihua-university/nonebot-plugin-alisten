"""Alisten 服务器 API 客户端"""

from datetime import datetime
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


class HouseInfo(BaseModel):
    """房间信息"""

    createTime: datetime
    desc: str
    enableStatus: bool
    id: str
    name: str
    needPwd: bool
    population: int


class HouseSearchResponse(BaseModel):
    """房间搜索响应"""

    code: str
    data: list[HouseInfo]
    message: str


class AlistenAPI:
    """Alisten API 客户端"""

    def __init__(self, config: AlistenConfig, session: UserSession):
        self.config = config
        self.session = session

    async def pick_music(self, name: str, source: str) -> SuccessResponse | ErrorResponse:
        """点歌

        Args:
            name: 音乐名称或搜索关键词
            source: 音乐源 (wy/qq/db)

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

        try:
            driver = cast("HTTPClientMixin", get_driver())

            # 创建请求对象
            request = Request(
                method="POST",
                url=f"{self.config.server_url}/music/pick",
                headers={"Content-Type": "application/json"},
                json=request_data.model_dump(),
            )

            response = await driver.request(request)
            if not response.content:
                return ErrorResponse(error="响应内容为空，请稍后重试")

            if response.status_code == 200:
                success_response = SuccessResponse.model_validate_json(response.content)
                return success_response

            else:
                error_response = ErrorResponse.model_validate_json(response.content)
                return error_response

        except Exception:
            logger.exception("Alisten API 请求失败")
            return ErrorResponse(error="请求失败，请稍后重试")

    async def house_search(self) -> HouseSearchResponse | ErrorResponse:
        """搜索房间列表

        Returns:
            房间列表或错误信息
        """
        try:
            driver = cast("HTTPClientMixin", get_driver())

            # 创建请求对象
            request = Request(
                method="GET",
                url=f"{self.config.server_url}/house/search",
                headers={"Content-Type": "application/json"},
            )

            response = await driver.request(request)
            if not response.content:
                return ErrorResponse(error="响应内容为空，请稍后重试")

            if response.status_code == 200:
                house_response = HouseSearchResponse.model_validate_json(response.content)
                return house_response
            else:
                error_response = ErrorResponse.model_validate_json(response.content)
                return error_response

        except Exception:
            logger.exception("Alisten API 房间搜索请求失败")
            return ErrorResponse(error="房间搜索请求失败，请稍后重试")

    async def house_info(self) -> HouseInfo | ErrorResponse:
        """获取当前配置房间的信息

        Returns:
            房间信息或错误信息
        """
        # 先获取房间列表
        search_result = await self.house_search()

        # 如果获取房间列表失败，直接返回错误
        if isinstance(search_result, ErrorResponse):
            return search_result

        # 在房间列表中查找匹配的房间
        for house in search_result.data:
            if house.id == self.config.house_id:
                return house

        # 如果没有找到匹配的房间，返回错误
        return ErrorResponse(error=f"未找到房间ID为 {self.config.house_id} 的房间")
