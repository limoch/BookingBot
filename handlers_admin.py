from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from keyboards import main_menu, services_kb, time_kb, back_menu, back_to_menu, approve_kb
from config import ADMIN_IDS
from database import get_bookings, delete_booking

router = Router()


# ---------- ADMIN PANEL ----------

@router.message(Command("admin"))
async def admin_panel(msg: Message):

    if msg.from_user.id not in ADMIN_IDS:
        return

    bookings = await get_bookings()

    if not bookings:
        await msg.answer("📭 Записей пока нет")
        return

    for b in bookings:

        book_id = b[0]
        user_id = b[1]
        name = b[2]
        service = b[3]
        date = b[4]
        time = b[5]
        status = b[6]

        # перевод статуса в текст
        if status == "pending":
            status_text = "⏳ Ожидает подтверждения"
        elif status == "approved":
            status_text = "✅ Подтверждена"
        elif status == "rejected":
            status_text = "❌ Отклонена"
        else:
            status_text = "❓ Неизвестно"

        text = (
            f"📅 Запись #{book_id}\n\n"
            f"👤 {name}\n"
            f"💅 {service}\n"
            f"📆 {date}\n"
            f"⏰ {time}\n\n"
            f"📊 Статус: {status_text}"
        )

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Удалить",
                        callback_data=f"delete_booking:{book_id}:{user_id}"
                    )
                ]
            ]
        )

        await msg.answer(text, reply_markup=kb)


# ---------- DELETE BOOKING ----------

@router.callback_query(F.data.startswith("delete_booking"))
async def delete_booking_handler(call: CallbackQuery):

    if call.from_user.id not in ADMIN_IDS:
        return

    data = call.data.split(":")

    book_id = int(data[1])
    user_id = int(data[2])

    # удаляем запись из базы
    await delete_booking(book_id)

    # уведомляем клиента
    try:
        await call.bot.send_message(
            user_id,
            "❌ Ваша запись была удалена администратором.\n\n"
            "Пожалуйста создайте новую запись.",
            reply_markup=back_to_menu()
        )
    except:
        pass

    # обновляем сообщение админа
    await call.message.edit_text(
        f"❌ Запись #{book_id} удалена"
    )