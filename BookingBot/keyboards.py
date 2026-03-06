from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SERVICES


def main_menu():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💅 Записаться", callback_data="book")],
            [InlineKeyboardButton(text="📸 Портфолио", callback_data="portfolio")],
            [InlineKeyboardButton(text="📅 Мои записи", callback_data="my_bookings")]
        ]
    )
    return kb


def back_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back_services")]
        ]
    )


def back_to_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В меню", callback_data="menu")]
        ]
    )


def services_kb():
    buttons = []

    for service in SERVICES:
        buttons.append(
            [InlineKeyboardButton(text=service, callback_data=f"service:{service}")]
        )

    buttons.append(
        [InlineKeyboardButton(text="⬅ Назад", callback_data="menu")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def time_kb(times):
    buttons = []

    for t in times:
        buttons.append(
            [InlineKeyboardButton(text=t, callback_data=f"time:{t}")]
        )

    buttons.append(
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back_services")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)