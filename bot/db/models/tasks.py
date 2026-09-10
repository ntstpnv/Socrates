from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.models.base import Base


if TYPE_CHECKING:
    from bot.db.models.tests import Test


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (UniqueConstraint("question", "test_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    question: Mapped[str] = mapped_column(Text)
    option1: Mapped[str] = mapped_column(Text)
    option2: Mapped[str] = mapped_column(Text)
    option3: Mapped[str] = mapped_column(Text)
    option4: Mapped[str] = mapped_column(Text)

    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"))

    test: Mapped["Test"] = relationship(back_populates="questions")
