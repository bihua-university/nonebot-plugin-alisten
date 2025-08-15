import sys
from pathlib import Path

import nonebot
import pytest
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebug import NONEBOT_INIT_KWARGS, NONEBOT_START_LIFESPAN
from nonebug.app import App
from pytest_asyncio import is_async_test
from pytest_mock import MockerFixture
from sqlalchemy import delete

HOME_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HOME_DIR))


def pytest_configure(config: pytest.Config) -> None:
    config.stash[NONEBOT_INIT_KWARGS] = {
        "driver": "~httpx",
        "superusers": ["10"],
        "alembic_startup_check": False,
        "alconna_cache_message": False,
    }
    # 如果不设置为 False，会运行插件的 on_startup 函数
    # 会导致 orm 的 init_orm 函数在 patch 之前被调用
    config.stash[NONEBOT_START_LIFESPAN] = False


def pytest_collection_modifyitems(items: list[pytest.Item]):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(scope="session", autouse=True)
async def after_nonebot_init(after_nonebot_init: None):
    # 加载适配器
    driver = nonebot.get_driver()
    driver.register_adapter(OneBotV11Adapter)

    # 加载插件
    nonebot.load_plugin("nonebot_plugin_alisten")


@pytest.fixture
async def app(app: App, tmp_path: Path, mocker: MockerFixture):
    from nonebot_plugin_orm import init_orm

    driver = nonebot.get_driver()
    # 清除连接钩子，现在 NoneBug 会自动触发 on_bot_connect
    driver._bot_connection_hook.clear()

    # 插件数据目录
    mocker.patch("nonebot_plugin_localstore.BASE_DATA_DIR", tmp_path / "data")
    mocker.patch("nonebot_plugin_localstore.BASE_CACHE_DIR", tmp_path / "cache")
    mocker.patch("nonebot_plugin_localstore.BASE_CONFIG_DIR", tmp_path / "config")
    mocker.patch("nonebot_plugin_orm._data_dir", tmp_path)

    await init_orm()

    return app


@pytest.fixture(autouse=True)
async def _default_user(app: App):
    """设置默认用户名"""

    # 添加 user 缓存
    from nonebot_plugin_user.utils import get_user, set_user_email, set_user_name

    await get_user("QQClient", "10")
    await set_user_name("QQClient", "10", "nickname")
    await set_user_email("QQClient", "10", "nickname@example.com")
    await get_user("QQClient", "10000")
    await set_user_name("QQClient", "10000", "nickname10000")

    # 添加 uninfo 缓存
    from nonebot_plugin_uninfo import Member, Scene, SceneType, Session, User
    from nonebot_plugin_uninfo.adapters import INFO_FETCHER_MAPPING

    uninfo_cache = INFO_FETCHER_MAPPING["OneBot V11"].session_cache
    uninfo_cache["group_10000_10"] = Session(
        self_id="123456",
        adapter="OneBot V11",
        scope="QQClient",
        scene=Scene(
            id="10000",
            type=SceneType.GROUP,
        ),
        user=User(id="10", name="nickname"),
        member=Member(
            user=User(id="10", name="nickname"),
        ),
    )
    uninfo_cache["group_10000_10000"] = Session(
        self_id="123456",
        adapter="OneBot V11",
        scope="QQClient",
        scene=Scene(
            id="10000",
            type=SceneType.GROUP,
        ),
        user=User(id="10000", name="nickname10000"),
        member=Member(
            user=User(id="10000", name="nickname10000"),
        ),
    )

    yield

    # 清除数据库
    from nonebot_plugin_orm import get_session
    from nonebot_plugin_user.models import Bind, User

    async with get_session() as session, session.begin():
        await session.execute(delete(User))
        await session.execute(delete(Bind))

    from nonebot_plugin_alisten.models import AlistenConfig

    async with get_session() as session, session.begin():
        await session.execute(delete(AlistenConfig))


@pytest.fixture
async def _configs(app: App, mocker: MockerFixture):
    from nonebot_plugin_orm import get_session

    from nonebot_plugin_alisten.models import AlistenConfig

    async with get_session() as session:
        session.add(
            AlistenConfig(
                session_id="QQClient_10000",
                server_url="http://localhost:8080",
                house_id="room123",
                house_password="password123",
            )
        )
        await session.commit()
