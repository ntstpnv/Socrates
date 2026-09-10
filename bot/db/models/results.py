from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.models.base import Base


if TYPE_CHECKING:
    from bot.db.models.groups import Group
    from bot.db.models.students import Student
    from bot.db.models.tests import Test


class Result(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger)
    full_name: Mapped[str] = mapped_column(Text)

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"))

    finished_at: Mapped[datetime]
    answers: Mapped[str] = mapped_column(Text)
    points: Mapped[int] = mapped_column(SmallInteger)
    feedback: Mapped[str] = mapped_column(Text)

    group: Mapped["Group"] = relationship(back_populates="results")
    student: Mapped["Student"] = relationship(back_populates="results")
    test: Mapped["Test"] = relationship(back_populates="results")
