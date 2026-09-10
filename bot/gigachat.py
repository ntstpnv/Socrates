from asyncio import Lock
from ssl import create_default_context
from time import time_ns
from uuid import uuid4

from aiohttp import ClientError, ClientSession, TCPConnector
from sqlalchemy import Row

from bot.caches.paths import Paths
from bot.caches.texts import UserText
from bot.middlewares import User
from bot.settings import AUTHORIZATION_KEY, logger


class GigaChat:
    _LOCK = Lock()

    _access_token: str | None = None
    _expires_at: int | None = None

    _SSL = create_default_context(cafile=Paths.CERTIFICATE)

    @classmethod
    async def _get_access_token(cls) -> str:
        async with cls._LOCK:
            if cls._access_token and time_ns() < cls._expires_at:
                return cls._access_token

            async with ClientSession(connector=TCPConnector(ssl=cls._SSL)) as session:
                async with session.post(
                    "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json",
                        "RqUID": f"{uuid4()}",
                        "Authorization": f"Basic {AUTHORIZATION_KEY}",
                    },
                    data={
                        "scope": "GIGACHAT_API_PERS",
                    },
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            cls._access_token = data["access_token"]
            cls._expires_at = data["expires_at"] * 1_000_000 - 60_000_000_000

            return data["access_token"]

    @classmethod
    async def ask(cls, user: User, answers: list[Row]) -> str:
        try:
            access_token = await cls._get_access_token()

            async with ClientSession(connector=TCPConnector(ssl=cls._SSL)) as session:
                async with session.post(
                    "https://api.giga.chat/v2/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {access_token}",
                    },
                    json={
                        "model": "GigaChat-2",
                        "messages": [
                            {
                                "role": "system",
                                "content": [
                                    {
                                        "text": UserText.PROMPT,
                                    },
                                ],
                            },
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "text": f"{answers}",
                                    },
                                ],
                            },
                        ],
                        "model_options": {
                            "temperature": 0.1,
                            "top_p": 0.9,
                            "max_tokens": 800,
                        },
                    },
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            return data["messages"][0]["content"][0]["text"]

        except (ClientError, KeyError, TypeError) as error:
            logger.info("%s:%s | %s:%s", user.id, user.full_name, user.payload.step, error)
            return "Не удалось сформировать рекомендации"
