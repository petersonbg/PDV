import asyncio
import sys
from pathlib import Path
from typing import Generator

import pytest
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.core import security
from app import main as main_module
from app import models  # noqa: F401
from app.api.deps import get_db
from app.db.base import Base
from app.main import app

security.pwd_context = CryptContext(schemes=["plaintext"], deprecated="auto")

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def _create_engine() -> AsyncEngine:
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    main_module.AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return engine


@pytest.fixture
def engine() -> Generator[AsyncEngine, None, None]:
    engine = asyncio.get_event_loop().run_until_complete(_create_engine())
    try:
        yield engine
    finally:
        asyncio.get_event_loop().run_until_complete(engine.dispose())


@pytest.fixture
def session_factory(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
def client(session_factory: sessionmaker) -> Generator[AsyncClient, None, None]:
    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield async_client
    finally:
        asyncio.get_event_loop().run_until_complete(async_client.aclose())
        app.dependency_overrides.clear()
