from datetime import datetime

from bot.caches.statements import UserStatement
from bot.settings import ASYNC_ENGINE


async def add_result(
    user_id: int,
    full_name: str,
    group_id: int,
    student_id: int,
    test_id: int,
    finished_at: datetime,
    answers: str,
    points: int,
    feedback: str,
) -> None:
    async with ASYNC_ENGINE.begin() as async_connection:
        await async_connection.exec_driver_sql(
            UserStatement.ADD_RESULT,
            (
                user_id,
                full_name,
                group_id,
                student_id,
                test_id,
                finished_at,
                answers,
                points,
                feedback,
            ),
        )
