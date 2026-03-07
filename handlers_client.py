from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from database import add_booking, get_busy_times, get_user_booking, get_user_bookings, approve_booking_db, reject_booking_db
from keyboards import main_menu, services_kb, time_kb, back_menu, back_to_menu, approve_kb
from config import WORK_START, WORK_END, PORTFOLIO
from scheduler import schedule_reminder
from config import ADMIN_IDS

router = Router()

user_data = {}
portfolio_index = {}


# START
@router.message(Command("start"))
async def start(msg: Message):  

    await msg.answer(
        "Добро пожаловать 💅\n\nВыберите действие",
        reply_markup=main_menu()
    )


# ---------- PORTFOLIO ----------

def portfolio_kb(index):

    buttons = []

    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅", callback_data="portfolio_prev"))

    if index < len(PORTFOLIO) - 1:
        buttons.append(InlineKeyboardButton(text="➡", callback_data="portfolio_next"))

    nav = [b for b in buttons]

    keyboard = []

    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton(text="🏠 В меню", callback_data="menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(F.data == "portfolio")
async def portfolio(call: CallbackQuery):

    await call.answer()

    portfolio_index[call.from_user.id] = 0

    media = InputMediaPhoto(
        media=PORTFOLIO[0],
        caption="📸 Наши работы"
    )

    await call.message.edit_media(
        media,
        reply_markup=portfolio_kb(0)
    )


@router.callback_query(F.data == "portfolio_next")
async def portfolio_next(call: CallbackQuery):

    await call.answer()

    index = portfolio_index.get(call.from_user.id, 0) + 1

    portfolio_index[call.from_user.id] = index

    media = InputMediaPhoto(
        media=PORTFOLIO[index],
        caption=f"📸 Работа {index+1}/{len(PORTFOLIO)}"
    )

    await call.message.edit_media(
        media,
        reply_markup=portfolio_kb(index)
    )


@router.callback_query(F.data == "portfolio_prev")
async def portfolio_prev(call: CallbackQuery):

    await call.answer()

    index = portfolio_index.get(call.from_user.id, 0) - 1

    portfolio_index[call.from_user.id] = index

    media = InputMediaPhoto(
        media=PORTFOLIO[index],
        caption=f"📸 Работа {index+1}/{len(PORTFOLIO)}"
    )

    await call.message.edit_media(
        media,
        reply_markup=portfolio_kb(index)
    )


# ---------- MENU ----------

@router.callback_query(F.data == "menu")
async def back_menu_handler(call: CallbackQuery):

    await call.answer()

    # если сообщение содержит фото
    if call.message.photo:

        await call.message.delete()

        await call.message.answer(
            "Главное меню",
            reply_markup=main_menu()
        )

    # если обычное текстовое сообщение
    else:

        await call.message.edit_text(
            "Главное меню",
            reply_markup=main_menu()
        )


# ---------- SERVICES ----------

@router.callback_query(F.data == "book")
async def choose_service(call: CallbackQuery):

    await call.answer()

    await call.message.edit_text(
        "💅 Выберите услугу",
        reply_markup=services_kb()
    )


@router.callback_query(F.data == "back_services")
async def back_services(call: CallbackQuery):

    await call.answer()

    await call.message.edit_text(
        "💅 Выберите услугу",
        reply_markup=services_kb()
    )

# ---------- DATE ----------

@router.callback_query(F.data.startswith("service"))
async def choose_date(call: CallbackQuery):

    await call.answer()

    service = call.data.split(":")[1]

    user_data[call.from_user.id] = {"service": service}

    booking = await get_user_booking(call.from_user.id, service)

    if booking:

        date, time = booking

        await call.message.edit_text(
            f"❗ Вы уже записаны\n\n"
            f"💅 Услуга: {service}\n"
            f"📅 Дата: {date}\n"
            f"⏰ Время: {time}",
            reply_markup=back_menu()
        )

        return

    today = datetime.now().date()

    buttons = []

    for i in range(5):

        d = today + timedelta(days=i)

        buttons.append([
            InlineKeyboardButton(
                text=d.strftime("%d.%m"),
                callback_data=f"date:{d}"
            )
        ])

    # добавляем кнопку назад
    buttons.append([
        InlineKeyboardButton(
            text="⬅ Назад",
            callback_data="back_services"
        )
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await call.message.edit_text(
        "📅 Выберите дату",
        reply_markup=kb
    )


# ---------- TIME ----------

class BookingState(StatesGroup):
    waiting_for_name = State()


@router.callback_query(F.data.startswith("date"))
async def choose_time(call: CallbackQuery):

    await call.answer()

    date = call.data.split(":")[1]

    user_data[call.from_user.id]["date"] = date

    busy = await get_busy_times(date)

    times = []

    for h in range(WORK_START, WORK_END):

        t = f"{h:02d}:00"

        if t not in busy:
            times.append(t)

    await call.message.edit_text(
        "⏰ Свободные окна",
        reply_markup=time_kb(times)
    )


# ---------- CONFIRM ----------

@router.callback_query(F.data.startswith("time"))
async def ask_name_after_time(call: CallbackQuery, state: FSMContext):
    await call.answer()

    selected_time = call.data.replace("time:", "")
    user_data[call.from_user.id]["time"] = selected_time

    await state.set_state(BookingState.waiting_for_name)

    await call.message.edit_text(
        "✍️ На какое имя вас записать?\n\nВведите имя:"
    )

@router.message(BookingState.waiting_for_name)
async def confirm_booking(msg: Message, state: FSMContext):

    name = msg.text.strip()
    user_data[msg.from_user.id]["name"] = name

    data = user_data[msg.from_user.id]

    # создаём запись (со статусом pending)
    booking_id = await add_booking(
        msg.from_user.id,
        data["name"],
        data["service"],
        data["date"],
        data["time"]
    )

    # клавиатура подтверждения для админа
    approve_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять",
                    callback_data=f"approve:{booking_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"reject:{booking_id}"
                )
            ]
        ]
    )

    # отправляем заявку админам
    for admin_id in ADMIN_IDS:
        try:
            await msg.bot.send_message(
                admin_id,
                f"📌 Новая заявка на запись\n\n"
                f"👤 Клиент: {data['name']}\n"
                f"🆔 Telegram: {msg.from_user.id}\n"
                f"💅 Услуга: {data['service']}\n"
                f"📆 Дата: {data['date']}\n"
                f"⏰ Время: {data['time']}",
                reply_markup=approve_keyboard
            )
        except Exception as e:
            print(f"Ошибка отправки админу {admin_id}: {e}")

    # сообщение пользователю
    await msg.answer(
        f"⏳ Заявка отправлена мастеру\n\n"
        f"💅 Услуга: {data['service']}\n"
        f"📆 Дата: {data['date']}\n"
        f"⏰ Время: {data['time']}\n\n"
        f"Пожалуйста дождитесь подтверждения записи.",
        reply_markup=back_to_menu()
    )

    await state.clear()


@router.callback_query(F.data.startswith("approve"))
async def approve_booking(call: CallbackQuery):

    await call.answer()

    booking_id = call.data.split(":")[1]

    booking = await approve_booking_db(booking_id)

    if not booking:
        await call.message.edit_text("Запись не найдена")
        return

    user_id, service, date, time = booking

    await call.bot.send_message(
        user_id,
        f"✅ Ваша запись подтверждена!\n\n"
        f"💅 {service}\n"
        f"📆 {date}\n"
        f"⏰ {time}",
        reply_markup=back_to_menu()
    )

    await call.message.edit_text("✅ Запись подтверждена")


@router.callback_query(F.data.startswith("reject"))
async def reject_booking(call: CallbackQuery):

    await call.answer()

    booking_id = call.data.split(":")[1]

    booking = await reject_booking_db(booking_id)

    if not booking:
        await call.message.edit_text("Запись не найдена")
        return

    user_id, service, date, time = booking

    await call.bot.send_message(
        user_id,
        f"❌ К сожалению запись отклонена\n\n"
        f"💅 {service}\n"
        f"📆 {date}\n"
        f"⏰ {time}\n\n"
        f"Попробуйте выбрать другое время.",
        reply_markup=back_to_menu()
    )

    await call.message.edit_text("❌ Запись отклонена")


# ---------- MY BOOKINGS ----------

@router.callback_query(F.data == "my_bookings")
async def my_bookings(call: CallbackQuery):

    await call.answer()

    bookings = await get_user_bookings(call.from_user.id)

    if not bookings:

        await call.message.edit_text(
            "📭 У вас пока нет записей",
            reply_markup=back_to_menu()
        )

        return

    text = "📅 Ваши записи\n\n"

    for service, date, time in bookings:

        text += (
            f"💅 {service}\n"
            f"📆 {date}\n"
            f"⏰ {time}\n\n"
        )

    await call.message.edit_text(
        text,
        reply_markup=back_to_menu()
    )