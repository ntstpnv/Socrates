from asyncio import run
from json import load

from bot.caches.paths import Paths
from bot.db.models import Task, Test
from bot.settings import ASYNC_SESSION
from sqlalchemy import select


async def add_tests() -> None:
    async with ASYNC_SESSION.begin() as session:
        for path in Paths.TESTS.glob("*.json"):
            stmt = select(Test).where(Test.name == path.stem)
            result = await session.execute(stmt)
            test = result.scalar_one_or_none()

            if not test:
                test = Test(name=path.stem)
                session.add(test)
                await session.flush()

                with open(path, encoding="utf-8") as file:
                    tasks = load(file)

                for task_id, task in tasks.items():
                    session.add(
                        Task(
                            id=int(task_id),
                            question=task["0"],
                            option1=task["1"],
                            option2=task["2"],
                            option3=task["3"],
                            option4=task["4"],
                            test_id=test.id,
                        )
                    )


if __name__ == "__main__":
    run(add_tests())
