from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from models import Base, Subs, User

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db/twitter_db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        alice = User(name="Alice",   api_key="test")
        bob = User(name="Bob",     api_key="test2")
        charlie = User(name="Charlie", api_key="test3")
        session.add_all([alice, bob, charlie])
        await session.flush()


        session.add_all([
            Subs(follower_id=alice.id, following_id=bob.id),
            Subs(follower_id=alice.id, following_id=charlie.id),
            Subs(follower_id=bob.id, following_id=alice.id),
            Subs(follower_id=charlie.id, following_id=alice.id),
        ])
        await session.commit()


# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
