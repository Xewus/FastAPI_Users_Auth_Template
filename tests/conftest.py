import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.services import get_avatars_root
from src.db import Base
from src.db.database import get_db
from src.main import app

TEMP_MEDIA_DIR = Path(__file__).parent.resolve() / 'media'
TEMP_AVATARS_DIR = TEMP_MEDIA_DIR / 'avatars'

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
    autoflush=False,
    autocommit=False
)


async def get_test_db() -> AsyncSession:
    try:
        db = TestSession()
        yield db
    finally:
        await db.close()


@app.on_event('startup')
async def init_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.on_event('shutdown')
async def drop_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session', name='http_client')
def get_http_client():
    TEMP_MEDIA_DIR.mkdir()
    TEMP_AVATARS_DIR.mkdir()

    with TestClient(app) as client:
        app.dependency_overrides[get_db] = get_test_db
        app.dependency_overrides[get_avatars_root] = lambda: TEMP_AVATARS_DIR
        yield client
        app.dependency_overrides.clear()

    shutil.rmtree(TEMP_AVATARS_DIR)
    shutil.rmtree(TEMP_MEDIA_DIR)
