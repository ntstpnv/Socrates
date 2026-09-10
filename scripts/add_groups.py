from asyncio import run

from bot.db.models import Group, Student
from bot.settings import ASYNC_SESSION
from sqlalchemy import select


async def add_groups(new_groups: dict[str, list[str]]) -> None:
    async with ASYNC_SESSION.begin() as session:
        for new_group, new_students in new_groups.items():
            stmt = select(Group).where(Group.name == new_group)
            result = await session.execute(stmt)
            group = result.scalar_one_or_none()

            if not group:
                group = Group(name=new_group)
                session.add(group)

            for new_student in new_students:
                stmt = select(Student).where(Student.name == new_student, Student.group == group)
                result = await session.execute(stmt)
                student = result.scalar_one_or_none()

                if not student:
                    student = Student(name=new_student, group=group)
                    session.add(student)


if __name__ == "__main__":
    run(
        add_groups(
            {
                "": [],
            }
        )
    )
