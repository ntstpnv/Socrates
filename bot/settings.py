from asyncio import Lock
from logging import INFO, basicConfig, getLogger
from os import getenv

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.caches.paths import Paths


def read_secret(secret: str) -> str:
    with open(Paths.SECRETS / secret, encoding="utf-8") as file:
        return file.read().strip()


DB_PASS = read_secret("db_password")
DB_HOST = getenv("DB_HOST", "localhost")

DSN = f"postgresql+asyncpg://postgres:{DB_PASS}@{DB_HOST}:5432/postgres"

ASYNC_ENGINE = create_async_engine(DSN)

ASYNC_SESSION = async_sessionmaker(ASYNC_ENGINE)

TOKEN = read_secret("bot_token")

ADMINS = {int(user_id) for user_id in read_secret("bot_admins").split(",")}

AUTHORIZATION_KEY = read_secret("gigachat_token")

LOCKS: dict[int, Lock] = {}

basicConfig(
    format="%(asctime)s | %(name)-10s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S %d.%m.%Y",
    level=INFO,
)

logger = getLogger("bot")
