from typing import TYPE_CHECKING

from sqlalchemy import SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.models.base import Base


if TYPE_CHECKING:
    from bot.db.models.results import Result
    from bot.db.models.tasks import Task


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    name: Mapped[str] = mapped_column(Text, unique=True)

    questions: Mapped[set["Task"]] = relationship(back_populates="test")
    results: Mapped[set["Result"]] = relationship(back_populates="test")
