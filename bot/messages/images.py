from asyncio import get_running_loop
from io import BytesIO

from maxapi.types import InputMediaBuffer
from PIL import Image, ImageDraw, ImageFont

from bot.caches.paths import Paths


class ImageFactory:
    _BACKGROUND = Image.new("RGB", (1000, 1000), color="white")
    _XY = (0, 0)
    _FONT = ImageFont.truetype(Paths.FONT, 38)
    _FORMAT = "WEBP"

    EXECUTOR = None

    @classmethod
    def _create(cls, text: str) -> bytes:
        image = cls._BACKGROUND.copy()
        ImageDraw.Draw(image).multiline_text(cls._XY, text, "black", cls._FONT)
        buffer = BytesIO()
        image.save(buffer, cls._FORMAT)

        return buffer.getvalue()

    @classmethod
    async def _to_bytes(cls, text: str) -> bytes:
        return await get_running_loop().run_in_executor(cls.EXECUTOR, cls._create, text)

    @classmethod
    async def from_text(cls, text: str) -> InputMediaBuffer:
        return InputMediaBuffer(await cls._to_bytes(text))
