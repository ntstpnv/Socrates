from asyncio import Lock
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from maxapi.context import MemoryContext
from maxapi.types import MessageCallback

from bot.messages.buttons import Payload
from bot.settings import LOCKS, logger


type Input = Callable[[MessageCallback, MemoryContext, Payload], Awaitable[None]]
type Output = Callable[[MessageCallback, MemoryContext, User], Awaitable[None]]


class User:
    __slots__ = ("id", "full_name", "payload", "next_step", "data")

    def __init__(self, event: MessageCallback, payload: Payload) -> None:
        self.id = event.callback.user.user_id
        self.full_name = event.callback.user.full_name

        self.payload = payload
        self.next_step = payload.step + 1


@asynccontextmanager
async def _transact(context: MemoryContext, user: User) -> AsyncIterator[None]:
    await context.update_data(step=user.next_step)
    try:
        yield
    except Exception:
        await context.update_data(step=user.payload.step)
        raise


def callback_lock(handler: Output) -> Input:
    async def wrapper(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
        user = User(event, payload)

        logger.info("%s:%s | %s:enter", user.id, user.full_name, user.payload.step)

        async with LOCKS.setdefault(user.id, Lock()):
            user.data = await context.get_data()

            if user.payload.step != user.data.get("step", 1):
                logger.info("%s:%s | %s:debounce", user.id, user.full_name, user.payload.step)
                return None

            async with _transact(context, user):
                return await handler(event, context, user)

    return wrapper
