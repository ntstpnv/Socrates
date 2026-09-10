from sqlalchemy import Row

from bot.settings import ASYNC_ENGINE


async def get_rows(statement: str, *args) -> list[Row]:
    async with ASYNC_ENGINE.connect() as async_connection:
        results = await async_connection.exec_driver_sql(statement, args)
        rows = results.all()

    return rows
