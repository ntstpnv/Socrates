from asyncio import run

from bot.db.models import Base
from bot.settings import ASYNC_ENGINE


async def create_tables() -> None:
    async with ASYNC_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    run(create_tables())
