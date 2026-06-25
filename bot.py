import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, QUESTIONS
from sheets import append_row, apply_conditional_formatting, set_font_size

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

TOTAL_STEPS = len(QUESTIONS)


class OrderForm(StatesGroup):
    account = State()
    name = State()
    category = State()
    article = State()
    quantity = State()
    buyout = State()
    price = State()
    total = State()


QUESTIONS_MAP = [
    OrderForm.account,
    OrderForm.name,
    OrderForm.category,
    OrderForm.article,
    OrderForm.quantity,
    OrderForm.buyout,
    OrderForm.price,
    OrderForm.total,
]

BUYOUT_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Самовыкуп", callback_data="buyout_sam"),
            InlineKeyboardButton(text="Раздача", callback_data="buyout_raz"),
        ]
    ]
)

START_MSG = (
    "<b>Добро пожаловать!</b>\n\n"
    "Заполни данные для новой записи в таблице.\n"
    "<i>Напиши /cancel чтобы отменить</i>\n\n"
    "{question}"
)

STEP_MSG = "<b>Шаг {step}/{total}</b>\n\n{question}"

DONE_MSG = (
    "<b>Запись добавлена в таблицу!</b>\n\n"
    "Дата: {date}\n"
    "Аккаунт: {account}\n"
    "Имя: {name}\n"
    "Категория: {category}\n"
    "Артикул: {article}\n"
    "Штук: {quantity}\n"
    "Самовыкуп/раздача: {buyout}\n"
    "Цена за шт/тг: {price}\n"
    "Общая сумма: {total}\n\n"
    "Напиши /start чтобы добавить ещё."
)

CANCEL_MSG = "<b>Отменено.</b>"


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(QUESTIONS_MAP[0])
    await message.answer(START_MSG.format(question=QUESTIONS[0]))


@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(CANCEL_MSG, reply_markup=types.ReplyKeyboardRemove())


@dp.message(OrderForm.account)
async def process_account(message: types.Message, state: FSMContext):
    await state.update_data(account=message.text)
    await state.set_state(QUESTIONS_MAP[1])
    await message.answer(STEP_MSG.format(step=2, total=TOTAL_STEPS, question=QUESTIONS[1]))


@dp.message(OrderForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(QUESTIONS_MAP[2])
    await message.answer(STEP_MSG.format(step=3, total=TOTAL_STEPS, question=QUESTIONS[2]))


@dp.message(OrderForm.category)
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(QUESTIONS_MAP[3])
    await message.answer(STEP_MSG.format(step=4, total=TOTAL_STEPS, question=QUESTIONS[3]))


@dp.message(OrderForm.article)
async def process_article(message: types.Message, state: FSMContext):
    await state.update_data(article=message.text)
    await state.set_state(QUESTIONS_MAP[4])
    await message.answer(STEP_MSG.format(step=5, total=TOTAL_STEPS, question=QUESTIONS[4]))


@dp.message(OrderForm.quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    await state.set_state(QUESTIONS_MAP[5])
    await message.answer(
        STEP_MSG.format(step=6, total=TOTAL_STEPS, question=QUESTIONS[5]),
        reply_markup=BUYOUT_KEYBOARD,
    )


@dp.callback_query(lambda c: c.data in ("buyout_sam", "buyout_raz"))
async def process_buyout_callback(callback: types.CallbackQuery, state: FSMContext):
    value = "Самовыкуп" if callback.data == "buyout_sam" else "Раздача"
    await state.update_data(buyout=value)
    await state.set_state(QUESTIONS_MAP[6])
    await callback.message.edit_text(
        STEP_MSG.format(step=7, total=TOTAL_STEPS, question=QUESTIONS[6]),
        reply_markup=None,
    )
    await callback.answer()


@dp.message(OrderForm.price)
async def process_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(QUESTIONS_MAP[7])
    await message.answer(STEP_MSG.format(step=8, total=TOTAL_STEPS, question=QUESTIONS[7]))


@dp.message(OrderForm.total)
async def process_total(message: types.Message, state: FSMContext):
    data = await state.update_data(total=message.text)
    data["date"] = datetime.now().strftime("%d.%m.%Y %H:%M")
    await state.clear()

    row = [
        data["account"],
        data["name"],
        data["category"],
        data["article"],
        data["quantity"],
        data["buyout"],
        data["price"],
        data["total"],
        data["date"],
    ]

    try:
        append_row(row)
        await message.answer(DONE_MSG.format(**data))
    except Exception as e:
        logging.error(e)
        await message.answer(
            "<b>Ошибка при сохранении в таблицу.</b>\n"
            "Попробуй ещё раз /start"
        )


async def main():
    try:
        apply_conditional_formatting()
        logging.info("Conditional formatting applied")
    except Exception as e:
        logging.warning("Could not apply conditional formatting: %s", e)
    try:
        set_font_size(14)
        logging.info("Font size set to 14")
    except Exception as e:
        logging.warning("Could not set font size: %s", e)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
