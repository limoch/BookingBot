import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import init_db
from scheduler import start
import handlers_client
import handlers_admin


async def main():

    bot = Bot(BOT_TOKEN)

    dp = Dispatcher()

    dp.include_router(handlers_client.router)
    dp.include_router(handlers_admin.router)

    await init_db()

    start()

    print("BOT STARTED")

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())