from asyncio import run
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from multiprocessing import get_context
from os import cpu_count
from random import choice
from time import perf_counter

from maxapi import Bot, Dispatcher
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.enums import ChatType, ParseMode
from maxapi.filters.command import Command, CommandStart
from maxapi.types import InputMediaBuffer, MessageCallback, MessageCreated

from bot.caches.permutations import PERMUTATIONS
from bot.caches.progress_bars import PROGRESS_BARS
from bot.caches.statements import AdminStatement, UserStatement
from bot.caches.texts import AdminText, CommonText, UserText
from bot.db.queries.results import add_result
from bot.db.queries.rows import get_rows
from bot.gigachat import GigaChat
from bot.messages.attachments import AttachmentFactory
from bot.messages.buttons import Payload
from bot.messages.images import ImageFactory
from bot.messages.texts import TextFactory
from bot.middlewares import User, callback_lock
from bot.settings import ADMINS, LOCKS, TOKEN, logger


bot = Bot(TOKEN, format=ParseMode.HTML, auto_requests=False)
dp = Dispatcher()


class AdminState(StatesGroup):
    ADMIN2 = State()
    ADMIN3 = State()
    ADMIN4 = State()


class UserState(StatesGroup):
    USER2 = State()
    USER3 = State()
    USER4 = State()
    USER5 = State()
    USER6 = State()


@dp.message_created(None, Command("admin"))
async def admin_selects_group(event: MessageCreated, context: MemoryContext) -> None:
    if not event.message.sender:
        return

    user_id = event.message.sender.user_id
    full_name = event.message.sender.full_name
    is_admin = user_id in ADMINS

    logger.info("%s:%s | 1:is_admin=%s", user_id, full_name, is_admin)

    if not is_admin:
        return

    groups = await get_rows(AdminStatement.GET_GROUPS)
    attachments = AttachmentFactory.from_rows(1, groups)

    message = await event.message.answer(AdminText.SELECT_GROUP, attachments)

    if message is None or message.message.body is None:
        return

    await context.set_data({"message_id": message.message.body.mid})

    await context.set_state(AdminState.ADMIN2)


@dp.message_callback(AdminState.ADMIN2, Payload.filter())
@callback_lock
async def admin_selects_test(event: MessageCallback, context: MemoryContext, user: User) -> None:
    await context.update_data(group_id=user.payload.id, group=user.payload.value)

    tests = await get_rows(AdminStatement.GET_TESTS, user.payload.id)
    attachments = AttachmentFactory.from_rows(user.next_step, tests)

    await event.edit(AdminText.SELECT_TEST, attachments)

    await context.set_state(AdminState.ADMIN3)


@dp.message_callback(AdminState.ADMIN3, Payload.filter())
@callback_lock
async def admin_confirms_selection(event: MessageCallback, context: MemoryContext, user: User) -> None:
    await context.update_data(test_id=user.payload.id, test=user.payload.value)

    text = AdminText.CONFIRM.format(user.data["group"], user.payload.value)

    attachments = AttachmentFactory.for_confirmation(user.next_step)

    await event.edit(text, attachments)

    await context.set_state(AdminState.ADMIN4)


@dp.message_callback(AdminState.ADMIN4, Payload.filter())
@callback_lock
async def admin_gets_results(event: MessageCallback, context: MemoryContext, user: User) -> None:
    if user.payload.id:
        await event.edit(CommonText.STOP, [])
        await clear(user.id, user.full_name, user.payload.step, context)
        return

    results = await get_rows(AdminStatement.GET_RESULTS, user.data["group_id"], user.data["test_id"])

    texts = [f"Группа: {user.data['group']}", f"Тест: {user.data['test']}\n"]
    for r in results:
        if r.user_id:
            mistakes = " ".join(a for a in r.answers.split() if not a.endswith("1"))
            mistakes = mistakes + "\n" if mistakes else ""
            texts.append(f"{r.name}: {r.points} из 30\n{r.user_id} {r.full_name}\n{mistakes}")
        else:
            texts.append(f"{r.name}\n")

    text = "\n".join(texts)
    attachments = [InputMediaBuffer(text.encode("utf-8-sig"), "results.txt")]

    await event.delete()

    await event.send(CommonText.PLACEHOLDER, attachments)

    await clear(user.id, user.full_name, user.payload.step, context)


@dp.message_created(None, CommandStart())
async def user_selects_group(event: MessageCreated, context: MemoryContext) -> None:
    if event.message.recipient.chat_type != ChatType.DIALOG:
        return

    groups = await get_rows(UserStatement.GET_GROUPS)
    attachments = AttachmentFactory.from_rows(1, groups)

    message = await event.message.answer(UserText.SELECT_GROUP, attachments)

    if message is None or message.message.body is None:
        return

    await context.set_data({"message_id": message.message.body.mid})

    await context.set_state(UserState.USER2)


@dp.message_callback(UserState.USER2, Payload.filter())
@callback_lock
async def user_selects_student(event: MessageCallback, context: MemoryContext, user: User) -> None:
    await context.update_data(group_id=user.payload.id, group=user.payload.value)

    t1 = perf_counter()
    students = await get_rows(UserStatement.GET_STUDENTS, user.payload.id)
    t_get_rows = perf_counter() - t1

    attachments = AttachmentFactory.from_rows(user.next_step, students)

    t2 = perf_counter()
    await event.edit(UserText.SELECT_STUDENT, attachments)
    t_edit = perf_counter() - t2

    logger.info(
        "%s:%s | %s:get_rows=%.3fs, edit=%.3fs",
        user.id,
        user.full_name,
        user.payload.step,
        t_get_rows,
        t_edit,
    )

    await context.set_state(UserState.USER3)


@dp.message_callback(UserState.USER3, Payload.filter())
@callback_lock
async def user_selects_test(event: MessageCallback, context: MemoryContext, user: User) -> None:
    await context.update_data(student_id=user.payload.id, student=user.payload.value)

    t1 = perf_counter()
    tests = await get_rows(UserStatement.GET_TESTS)
    t_get_rows = perf_counter() - t1

    attachments = AttachmentFactory.from_rows(user.next_step, tests)

    t2 = perf_counter()
    await event.edit(UserText.SELECT_TEST, attachments)
    t_edit = perf_counter() - t2

    logger.info(
        "%s:%s | %s:get_rows=%.3fs, edit=%.3fs",
        user.id,
        user.full_name,
        user.payload.step,
        t_get_rows,
        t_edit,
    )

    await context.set_state(UserState.USER4)


@dp.message_callback(UserState.USER4, Payload.filter())
@callback_lock
async def user_confirms_selection(event: MessageCallback, context: MemoryContext, user: User) -> None:
    await context.update_data(test_id=user.payload.id, test=user.payload.value)

    text = UserText.CONFIRM.format(user.data["group"], user.data["student"], user.payload.value)

    attachments = AttachmentFactory.for_confirmation(user.next_step)

    t1 = perf_counter()
    await event.edit(text, attachments)
    t_edit = perf_counter() - t1

    logger.info(
        "%s:%s | %s:edit=%.3fs",
        user.id,
        user.full_name,
        user.payload.step,
        t_edit,
    )

    await context.set_state(UserState.USER5)


@dp.message_callback(UserState.USER5, Payload.filter())
@callback_lock
async def user_gets_first_question(event: MessageCallback, context: MemoryContext, user: User) -> None:
    if user.payload.id:
        await event.edit(CommonText.STOP, [])
        await clear(user.id, user.full_name, user.payload.step, context)
        return

    t1 = perf_counter()
    tasks = await get_rows(UserStatement.GET_TASKS, user.data["test_id"])
    t_get_rows = perf_counter() - t1

    texts, options = deque(), deque()

    for progress_bar, task in zip(PROGRESS_BARS, tasks):
        order = (task.option1, task.option2, task.option3, task.option4)
        to0from, to1from, to2from, to3from = choice(PERMUTATIONS)
        texts.append(
            TextFactory.for_task(
                progress_bar,
                task.question,
                order[to0from],
                order[to1from],
                order[to2from],
                order[to3from],
            )
        )
        options.append(
            (
                f"{task.id}-{to0from + 1}",
                f"{task.id}-{to1from + 1}",
                f"{task.id}-{to2from + 1}",
                f"{task.id}-{to3from + 1}",
            )
        )

    text = texts.popleft()

    await context.update_data(texts=texts, options=options, answers=[])

    t2 = perf_counter()
    attachments = await AttachmentFactory.for_task(user.next_step, text)
    t_attachments = perf_counter() - t2

    t3 = perf_counter()
    await event.edit(CommonText.PLACEHOLDER, attachments)
    t_edit = perf_counter() - t3

    logger.info(
        "%s:%s | %s:get_rows=%.3fs, attachments=%.3fs, edit=%.3fs",
        user.id,
        user.full_name,
        user.payload.step,
        t_get_rows,
        t_attachments,
        t_edit,
    )

    await context.set_state(UserState.USER6)


@dp.message_callback(UserState.USER6, Payload.filter())
@callback_lock
async def user_gets_next_question(event: MessageCallback, context: MemoryContext, user: User) -> None:
    t1 = perf_counter()
    await event.edit(CommonText.PROCESSING, [])
    t_edit1 = perf_counter() - t1

    user.data["answers"].append(user.data["options"].popleft()[user.payload.id])

    if not user.data["texts"]:
        finished_at = datetime.now()
        answers = sorted(user.data["answers"], key=lambda a: (len(a), a))
        points = sum(a.endswith("1") for a in answers)

        t2 = perf_counter()
        summary = await get_rows(UserStatement.GET_SUMMARY, answers)
        t_get_rows = perf_counter() - t2

        t3 = perf_counter()
        feedback = await GigaChat.ask(user, summary)
        t_ask = perf_counter() - t3

        t4 = perf_counter()
        await add_result(
            user.id,
            user.full_name,
            user.data["group_id"],
            user.data["student_id"],
            user.data["test_id"],
            finished_at,
            " ".join(answers),
            points,
            feedback,
        )
        t_add_result = perf_counter() - t4

        text = UserText.RESULT.format(
            user.data["group"],
            user.data["student"],
            user.data["test"],
            finished_at.strftime("%H:%M %d.%m.%Y"),
            points,
            feedback,
        )

        t5 = perf_counter()
        await event.edit(text, [])
        t_edit2 = perf_counter() - t5

        logger.info(
            "%s:%s | %s:edit1=%.3fs, get_rows=%.3fs, ask=%.3fs, add_result=%.3fs, edit2=%.3fs",
            user.id,
            user.full_name,
            user.payload.step,
            t_edit1,
            t_get_rows,
            t_ask,
            t_add_result,
            t_edit2,
        )

        await clear(user.id, user.full_name, user.payload.step, context)
        return

    text = user.data["texts"].popleft()

    await context.update_data(
        texts=user.data["texts"],
        options=user.data["options"],
        answers=user.data["answers"],
    )

    t2 = perf_counter()
    attachments = await AttachmentFactory.for_task(user.next_step, text)
    t_attachments = perf_counter() - t2

    t3 = perf_counter()
    await event.edit(CommonText.PLACEHOLDER, attachments)
    t_edit2 = perf_counter() - t3

    logger.info(
        "%s:%s | %s:edit1=%.3fs, attachments=%.3fs, edit2=%.3fs",
        user.id,
        user.full_name,
        user.payload.step,
        t_edit1,
        t_attachments,
        t_edit2,
    )


@dp.message_created(Command("stop"))
async def stop(event: MessageCreated, context: MemoryContext) -> None:
    if event.message.sender is None:
        return

    user_id = event.message.sender.user_id
    full_name = event.message.sender.full_name

    data = await context.get_data()

    if message_id := data.get("message_id", ""):
        await bot.edit_message(message_id, CommonText.STOP, [])

    await clear(user_id, full_name, data.get("step", 1), context)


async def clear(user_id: int, full_name: str, step: int, context: MemoryContext) -> None:
    await context.clear()
    LOCKS.pop(user_id, None)
    logger.info("%s:%s | %s:clear", user_id, full_name, step)


async def main():
    with ProcessPoolExecutor(cpu_count(), get_context("fork")) as executor:
        ImageFactory.EXECUTOR = executor
        await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    run(main())
