from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import ADMIN_IDS
from database import get_bookings, delete_booking

router = Router()


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
        name = b[2]
        service = b[3]
        date = b[4]
        time = b[5]

        text = (
            f"📅 Запись #{book_id}\n\n"
            f"👤 {name}\n"
            f"💅 {service}\n"
            f"📆 {date}\n"
            f"⏰ {time}"
        )

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Удалить",
                        callback_data=f"delete_booking:{book_id}"
                    )
                ]
            ]
        )

        await msg.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("delete_booking"))
async def delete_booking_handler(call: CallbackQuery):

    if call.from_user.id not in ADMIN_IDS:
        return

    book_id = int(call.data.split(":")[1])

    await delete_booking(book_id)

    await call.message.edit_text(
        f"❌ Запись #{book_id} удалена"
    )

