import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models import Base, User, Subs


DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():

    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):

    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as s:
        yield s


@pytest_asyncio.fixture
async def users(session):

    alice = User(name="Alice", api_key="test")
    bob = User(name="Bob", api_key="test2")
    charlie = User(name="Charlie", api_key="test3")
    session.add_all([alice, bob, charlie])
    await session.flush()

    session.add(Subs(follower_id=alice.id, following_id=bob.id))
    await session.commit()

    await session.refresh(alice)
    await session.refresh(bob)
    await session.refresh(charlie)
    return {"alice": alice, "bob": bob, "charlie": charlie}


@pytest_asyncio.fixture
async def client(engine):

    from main import app
    from database import get_session

    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_session():
        async with async_session() as s:
            yield s

    app.dependency_overrides[get_session] = override_get_session

    async with async_session() as s:
        alice = User(name="Alice", api_key="test")
        s.add(alice)
        await s.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()