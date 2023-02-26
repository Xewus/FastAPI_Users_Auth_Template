import shutil
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import AVATAR_SIZES
from src.core.services import get_avatars_root
from src.db import Base
from src.db.database import get_db
from src.main import app

MIN_SIZE_AVATAR = min(AVATAR_SIZES)

ROOT_DIR = Path(__file__).parent.resolve()
TEMP_MEDIA_DIR = ROOT_DIR / 'media'
TEMP_AVATARS_DIR = TEMP_MEDIA_DIR / 'avatars'
BIG_B64_IMAGE = ROOT_DIR / 'helpers' / 'big_b64_image'

test_engine = create_async_engine(
    # 'sqlite+aiosqlite:///./test.db',
    'sqlite+aiosqlite:///:memory:',
    connect_args={'check_same_thread': False},
    future=True,
    # echo=True,
)

TestSession = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


@pytest.fixture(scope='module')
def temp_dirs():
    if TEMP_MEDIA_DIR.exists():
        shutil.rmtree(TEMP_MEDIA_DIR)

    TEMP_MEDIA_DIR.mkdir()
    TEMP_AVATARS_DIR.mkdir()

    yield TEMP_AVATARS_DIR

    shutil.rmtree(TEMP_MEDIA_DIR)


async def get_test_db() -> AsyncSession:
    try:
        db = TestSession()
        yield db
    finally:
        await db.close()


@pytest.fixture(autouse=True)
async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(name='http_client')
def get_http_client(temp_dirs):
    with TestClient(app) as client:
        app.root_path
        app.dependency_overrides[get_db] = get_test_db
        app.dependency_overrides[get_avatars_root] = lambda: temp_dirs

        yield client

        app.dependency_overrides.clear()
