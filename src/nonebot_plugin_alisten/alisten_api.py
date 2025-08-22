"""Alisten 服务器 API 客户端"""

from datetime import datetime
from typing import TypeVar, cast

from nonebot import get_driver
from nonebot.drivers import HTTPClientMixin, Request
from nonebot.log import logger
from nonebot_plugin_user import UserSession
from pydantic import BaseModel

from .models import AlistenConfig

# 定义泛型类型
T = TypeVar("T", bound=BaseModel)


class ErrorResponse(BaseModel):
    """错误响应"""

    error: str


class MessageResponse(BaseModel):
    """消息响应"""

    message: str


class User(BaseModel):
    name: str
    email: str


class PickMusicRequest(BaseModel):
    """点歌请求"""

    houseId: str
    password: str = ""
    user: User
    id: str = ""
    name: str = ""
    source: str


class MusicData(BaseModel):
    """音乐数据"""

    name: str
    source: str
    id: str


class PickMusicResponse(BaseModel):
    """点歌响应"""

    code: str
    message: str
    data: MusicData


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


class DeleteMusicRequest(BaseModel):
    """删除音乐请求"""

    houseId: str
    password: str = ""
    id: str


class PlaylistRequest(BaseModel):
    """获取播放列表请求"""

    houseId: str
    password: str = ""


class PlaylistItem(BaseModel):
    """播放列表项"""

    name: str
    source: str
    id: str
    likes: int
    user: User


class PlaylistResponse(BaseModel):
    """播放列表响应"""

    playlist: list[PlaylistItem] | None = None


class HouseUserRequest(BaseModel):
    """获取房间用户请求"""

    houseId: str
    password: str = ""


class HouseUserResponse(BaseModel):
    """房间用户列表响应"""

    data: list[User] | None = None


class VoteSkipRequest(BaseModel):
    """投票跳过请求"""

    houseId: str
    password: str = ""
    user: User


class VoteSkipResponse(BaseModel):
    """投票跳过响应"""

    message: str
    current_votes: int | None = None


class GoodMusicRequest(BaseModel):
    """点赞音乐请求"""

    houseId: str
    password: str = ""
    index: int
    name: str


class GoodMusicResponse(BaseModel):
    """点赞音乐响应"""

    message: str
    likes: int


class SearchMusicRequest(BaseModel):
    """搜索音乐请求"""

    houseId: str
    password: str = ""
    name: str
    source: str


class SearchMusicItem(BaseModel):
    """搜索音乐结果项"""

    id: str
    name: str
    source: str


class SearchMusicResponse(BaseModel):
    """搜索音乐响应"""

    data: list[SearchMusicItem] | None = None


class CurrentMusicRequest(BaseModel):
    """获取当前音乐请求"""

    houseId: str
    password: str = ""


class CurrentMusicData(BaseModel):
    """当前音乐数据"""

    name: str
    source: str
    id: str
    user: User
    likes: int


class CurrentMusicResponse(BaseModel):
    """当前音乐响应"""

    data: CurrentMusicData | None = None


class AlistenAPI:
    """Alisten API 客户端"""

    def __init__(self, config: AlistenConfig, user_session: UserSession):
        self.config = config
        self.user_session = user_session

    async def _make_request(
        self, method: str, endpoint: str, response_type: type[T], error_msg: str, json_data: dict | None = None
    ) -> T | ErrorResponse:
        """通用的API请求处理方法

        Args:
            method: HTTP方法 (GET/POST)
            endpoint: API端点
            response_type: 期望的响应类型
            error_msg: 错误时的提示信息
            json_data: POST请求的JSON数据

        Returns:
            成功时返回指定类型的响应，失败时返回ErrorResponse
        """
        try:
            driver = cast("HTTPClientMixin", get_driver())

            headers = {"Content-Type": "application/json"}
            request = Request(
                method=method,
                url=f"{self.config.server_url}{endpoint}",
                headers=headers,
                json=json_data,
            )

            response = await driver.request(request)
            if not response.content:
                return ErrorResponse(error="响应内容为空，请稍后重试")

            if response.status_code == 200:
                return response_type.model_validate_json(response.content)
            else:
                return ErrorResponse.model_validate_json(response.content)

        except Exception:
            logger.exception(f"Alisten API {error_msg}")
            return ErrorResponse(error=f"{error_msg}，请稍后重试")

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

        # 检查房间列表是否为空
        if not search_result.data:
            return ErrorResponse(error="未找到任何房间")

        # 在房间列表中查找匹配的房间
        for house in search_result.data:
            if house.id == self.config.house_id:
                return house

        # 如果没有找到匹配的房间，返回错误
        return ErrorResponse(error=f"未找到房间ID为 {self.config.house_id} 的房间")

    async def pick_music(self, id: str, name: str, source: str) -> PickMusicResponse | ErrorResponse:
        """点歌. 可通过 ID 或名称点歌

        Args:
            id: 音乐 ID
            name: 音乐名称或搜索关键词
            source: 音乐源 (wy/qq/db)

        Returns:
            点歌结果
        """
        request_data = PickMusicRequest(
            houseId=self.config.house_id,
            password=self.config.house_password,
            user=User(name=self.user_session.user_name, email=self.user_session.user_email or ""),
            id=id,
            name=name,
            source=source,
        )

        return await self._make_request(
            method="POST",
            endpoint="/music/pick",
            response_type=PickMusicResponse,
            error_msg="点歌请求失败",
            json_data=request_data.model_dump(),
        )

    async def house_search(self) -> HouseSearchResponse | ErrorResponse:
        """搜索房间列表

        Returns:
            房间列表或错误信息
        """
        return await self._make_request(
            method="GET",
            endpoint="/house/search",
            response_type=HouseSearchResponse,
            error_msg="房间搜索请求失败",
        )

    async def delete_music(self, id: str) -> MessageResponse | ErrorResponse:
        """删除音乐

        Args:
            id: 要删除的音乐ID

        Returns:
            删除结果
        """
        request_data = DeleteMusicRequest(
            houseId=self.config.house_id,
            password=self.config.house_password,
            id=id,
        )

        return await self._make_request(
            method="POST",
            endpoint="/music/delete",
            response_type=MessageResponse,
            error_msg="删除音乐请求失败",
            json_data=request_data.model_dump(),
        )

    async def good_music(self, index: int, name: str) -> GoodMusicResponse | ErrorResponse:
        """点赞音乐

        Args:
            index: 音乐在播放列表中的索引位置（从1开始）
            name: 音乐名称

        Returns:
            点赞结果
        """
        request_data = GoodMusicRequest(
            houseId=self.config.house_id,
            password=self.config.house_password,
            index=index,
            name=name,
        )

        return await self._make_request(
            method="POST",
            endpoint="/music/good",
            response_type=GoodMusicResponse,
            error_msg="点赞音乐请求失败",
            json_data=request_data.model_dump(),
        )

    async def vote_skip(self) -> VoteSkipResponse | ErrorResponse:
        """投票跳过当前歌曲

        Returns:
            投票结果
        """
        request_data = VoteSkipRequest(
            houseId=self.config.house_id,
            password=self.config.house_password,
            user=User(name=self.user_session.user_name, email=self.user_session.user_email or ""),
        )

        return await self._make_request(
            method="POST",
            endpoint="/music/skip/vote",
            response_type=VoteSkipResponse,
            error_msg="投票跳过请求失败",
            json_data=request_data.model_dump(),
        )

    async def get_playlist(self) -> PlaylistResponse | ErrorResponse:
        """获取当前播放列表

        Returns:
            播放列表
        """
        request_data = PlaylistRequest(
            houseId=self.config.house_id,
            password=self.config.house_password,
        )

        return await self._make_request(
            method="POST",
            endpoint="/music/playlist",
            response_type=PlaylistResponse,
            error_msg="获取播放列表请求失败",
            json_data=request_data.model_dump(),
        )

    async def get_house_user(self) -> HouseUserResponse | ErrorResponse:
        """获取房间用户列表

        Returns:
            房间用户列表
        """
        request_data = HouseUserRequest(
            houseId=self.config.house_id,
            password=self.config.house_password,
        )

        return await self._make_request(
            method="POST",
            endpoint="/house/houseuser",
            response_type=HouseUserResponse,
            error_msg="获取房间用户请求失败",
            json_data=request_data.model_dump(),
        )

    async def search_music(self, name: str, source: str) -> SearchMusicResponse | ErrorResponse:
        """搜索音乐

        Args:
            name: 音乐名称或搜索关键词
            source: 音乐源 (wy/qq/db)

        Returns:
            搜索结果
        """
        request_data = SearchMusicRequest(
            houseId=self.config.house_id,
            password=self.config.house_password,
            name=name,
            source=source,
        )

        return await self._make_request(
            method="POST",
            endpoint="/music/search",
            response_type=SearchMusicResponse,
            error_msg="搜索音乐请求失败",
            json_data=request_data.model_dump(),
        )

    async def get_current_music(self) -> CurrentMusicResponse | ErrorResponse:
        """获取当前播放的音乐

        Returns:
            当前音乐信息
        """
        request_data = CurrentMusicRequest(
            houseId=self.config.house_id,
            password=self.config.house_password,
        )

        return await self._make_request(
            method="POST",
            endpoint="/music/sync",
            response_type=CurrentMusicResponse,
            error_msg="获取当前音乐请求失败",
            json_data=request_data.model_dump(),
        )
