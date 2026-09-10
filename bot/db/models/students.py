from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.models.base import Base


if TYPE_CHECKING:
    from bot.db.models.groups import Group
    from bot.db.models.results import Result


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (UniqueConstraint("name", "group_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(Text)

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))

    group: Mapped["Group"] = relationship(back_populates="students")
    results: Mapped[set["Result"]] = relationship(back_populates="student")
