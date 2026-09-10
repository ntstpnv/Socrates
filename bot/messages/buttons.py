from functools import lru_cache

from maxapi.filters.callback_payload import CallbackPayload
from maxapi.types import CallbackButton
from maxapi.types.attachments import AttachmentButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from sqlalchemy import Row


class Payload(CallbackPayload):
    step: int
    id: int
    value: str


class ButtonFactory:
    @classmethod
    def _create(cls, buttons: list[CallbackButton], sizes: int) -> AttachmentButton:
        attachment = InlineKeyboardBuilder()
        attachment.add(*buttons)
        attachment.adjust(sizes)

        return attachment.as_markup()

    @classmethod
    def _pack(cls, step: int, i: int, value: str) -> str:
        return Payload(step=step, id=i, value=value).pack()

    @classmethod
    def _to_button(cls, step: int, i: int, value: str) -> CallbackButton:
        return CallbackButton(text=value, payload=cls._pack(step, i, value))

    @classmethod
    def from_rows(cls, step: int, rows: list[Row], sizes: int) -> AttachmentButton:
        return cls._create([cls._to_button(step, row.id, row.name) for row in rows], sizes)

    @classmethod
    @lru_cache(maxsize=None)
    def from_items(cls, step: int, items: tuple[str, ...], sizes: int) -> AttachmentButton:
        return cls._create([cls._to_button(step, i, item) for i, item in enumerate(items)], sizes)
