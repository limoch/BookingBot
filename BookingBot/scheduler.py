from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

scheduler = AsyncIOScheduler()

def start():
    scheduler.start()


def schedule_reminder(bot, user_id, date, time):

    dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

    remind = dt - timedelta(hours=1)

    scheduler.add_job(
        send_reminder,
        "date",
        run_date=remind,
        args=[bot, user_id, time]
    )


async def send_reminder(bot, user_id, time):

    await bot.send_message(
        user_id,
        f"⏰ Напоминание!\n\nВы записаны сегодня в {time}"
    )