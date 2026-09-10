from functools import lru_cache

from maxapi.types import InputMediaBuffer
from maxapi.types.attachments import AttachmentButton
from sqlalchemy import Row

from bot.messages.buttons import ButtonFactory
from bot.messages.images import ImageFactory


class AttachmentFactory:
    _ITEMS = ("1", "2", "3", "4")

    @staticmethod
    def from_rows(step: int, rows: list[Row]) -> list[AttachmentButton]:
        return [ButtonFactory.from_rows(step, rows, 2)]

    @staticmethod
    @lru_cache(maxsize=None)
    def for_confirmation(step: int) -> list[AttachmentButton]:
        return [ButtonFactory.from_items(step, ("Все верно", "Выбрать заново"), 1)]

    @classmethod
    async def for_task(cls, step: int, text: str) -> list[AttachmentButton | InputMediaBuffer]:
        return [await ImageFactory.from_text(text), ButtonFactory.from_items(step, cls._ITEMS, 4)]
