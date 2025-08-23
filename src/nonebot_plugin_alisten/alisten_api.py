"""Alisten 服务器 API 客户端"""

from datetime import datetime
from typing import TypeVar, cast

from nonebot import get_driver
from nonebot.drivers import HTTPClientMixin, Request
from nonebot.log import logger
from nonebot_plugin_user import UserSession
from pydantic import BaseModel, Field, RootModel

from .models import AlistenConfig

# 定义泛型类型
T = TypeVar("T", bound=BaseModel)


class ErrorResponse(BaseModel):
    """错误响应"""

    error: str


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


class PickMusicResponse(BaseModel):
    """点歌响应"""

    name: str
    source: str
    id: str


class HouseInfo(BaseModel):
    """房间信息"""

    createTime: datetime
    desc: str
    enableStatus: bool
    id: str
    name: str
    needPwd: bool
    population: int


class HouseSearchResponse(RootModel):
    """房间搜索响应"""

    root: list[HouseInfo] = []


class DeleteMusicRequest(BaseModel):
    """删除音乐请求"""

    houseId: str
    password: str = ""
    id: str
    """虽然叫 ID 但其实是音乐名称"""


class DeleteMusicResponse(BaseModel):
    """删除音乐响应"""

    name: str


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


class HouseUserResponse(RootModel):
    """房间用户列表响应"""

    root: list[User] = []


class VoteSkipRequest(BaseModel):
    """投票跳过请求"""

    houseId: str
    password: str = ""
    user: User


class VoteSkipResponse(BaseModel):
    """投票跳过响应"""

    current_votes: int
    required_votes: int | None = None


class GoodMusicRequest(BaseModel):
    """点赞音乐请求"""

    houseId: str
    password: str = ""
    index: int
    name: str


class GoodMusicResponse(BaseModel):
    """点赞音乐响应"""

    name: str
    likes: int


class PlayModeRequest(BaseModel):
    """设置播放模式请求"""

    houseId: str
    password: str = ""
    mode: str


class PlayModeResponse(BaseModel):
    """设置播放模式响应"""

    mode: str


class SearchMusicRequest(BaseModel):
    """搜索音乐请求"""

    houseId: str
    password: str = ""
    name: str
    source: str
    pageSize: int = 10


class SearchMusicItem(BaseModel):
    """搜索音乐结果项"""

    id: str
    name: str
    artist: str


class SearchMusicResponse(BaseModel):
    """搜索音乐响应"""

    data: list[SearchMusicItem] = Field(default=[], alias="list")
    totalSize: int


class CurrentMusicRequest(BaseModel):
    """获取当前音乐请求"""

    houseId: str
    password: str = ""


class CurrentMusicResponse(BaseModel):
    """当前音乐响应"""

    name: str
    source: str
    id: str
    user: User


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

    async def house_houseuser(self) -> list[User] | ErrorResponse:
        """获取房间内用户列表

        Returns:
            房间用户列表或错误信息
        """
        request_data = HouseUserRequest(
            houseId=self.config.house_id,
            password=self.config.house_password,
        )

        result = await self._make_request(
            method="POST",
            endpoint="/house/houseuser",
            response_type=HouseUserResponse,
            error_msg="获取房间用户请求失败",
            json_data=request_data.model_dump(),
        )

        if isinstance(result, ErrorResponse):
            return result

        return result.root

    async def house_search(self) -> list[HouseInfo] | ErrorResponse:
        """搜索可用的房间列表

        Returns:
            房间列表或错误信息
        """
        result = await self._make_request(
            method="GET",
            endpoint="/house/search",
            response_type=HouseSearchResponse,
            error_msg="房间搜索请求失败",
        )

        if isinstance(result, ErrorResponse):
            return result

        return result.root

    async def music_delete(self, id: str) -> DeleteMusicResponse | ErrorResponse:
        """从播放列表中删除指定音乐

        Args:
            id: 要删除的音乐ID（虽然叫 ID 但其实是音乐名称）

        Returns:
            删除操作结果
        """
        request_data = DeleteMusicRequest(
            houseId=self.config.house_id,
            password=self.config.house_password,
            id=id,
        )

        return await self._make_request(
            method="POST",
            endpoint="/music/delete",
            response_type=DeleteMusicResponse,
            error_msg="删除音乐请求失败",
            json_data=request_data.model_dump(),
        )

    async def music_good(self, index: int, name: str) -> GoodMusicResponse | ErrorResponse:
        """对播放列表中的音乐进行点赞

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

    async def music_pick(self, id: str, name: str, source: str) -> PickMusicResponse | ErrorResponse:
        """添加音乐到播放列表（点歌）

        Args:
            id: 音乐ID（可选，为空时使用名称搜索）
            name: 音乐名称或搜索关键词
            source: 音乐源（wy=网易云音乐，qq=QQ音乐，db=酷狗音乐）

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

    async def music_playlist(self) -> PlaylistResponse | ErrorResponse:
        """获取房间当前播放列表

        Returns:
            播放列表详情，包含歌曲信息和点赞数
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

    async def music_playmode(self, mode: str) -> PlayModeResponse | ErrorResponse:
        """设置房间播放模式

        Args:
            mode: 播放模式（0=顺序播放，1=随机播放）

        Returns:
            设置结果
        """
        request_data = PlayModeRequest(
            houseId=self.config.house_id,
            password=self.config.house_password,
            mode=mode,
        )

        return await self._make_request(
            method="POST",
            endpoint="/music/playmode",
            response_type=PlayModeResponse,
            error_msg="设置播放模式请求失败",
            json_data=request_data.model_dump(),
        )

    async def music_search(self, name: str, source: str) -> SearchMusicResponse | ErrorResponse:
        """在指定音乐平台搜索音乐

        Args:
            name: 音乐名称或搜索关键词
            source: 音乐源（wy=网易云音乐，qq=QQ音乐，db=酷狗音乐）

        Returns:
            搜索结果列表
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

    async def music_skip_vote(self) -> VoteSkipResponse | ErrorResponse:
        """投票跳过当前播放的歌曲

        Returns:
            投票结果，包含当前票数和所需票数
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

    async def music_sync(self) -> CurrentMusicResponse | ErrorResponse:
        """获取当前正在播放的音乐信息

        Returns:
            当前音乐详细信息
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
