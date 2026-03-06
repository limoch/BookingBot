import aiosqlite

DB = "booking.db"


async def init_db():
    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS bookings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            service TEXT,
            date TEXT,
            time TEXT
        )
        """)

        await db.commit()


async def add_booking(user_id, name, service, date, time):

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        INSERT INTO bookings (user_id,name,service,date,time)
        VALUES (?,?,?,?,?)
        """, (user_id, name, service, date, time))

        await db.commit()


async def get_bookings():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute("SELECT * FROM bookings")
        return await cursor.fetchall()


async def delete_booking(book_id):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "DELETE FROM bookings WHERE id=?",
            (book_id,)
        )

        await db.commit()


async def get_busy_times(date):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT time FROM bookings WHERE date=?",
            (date,)
        )

        rows = await cursor.fetchall()

        return [r[0] for r in rows]


# Проверка: записан ли пользователь на услугу
async def get_user_booking(user_id, service):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT date, time FROM bookings WHERE user_id=? AND service=?",
            (user_id, service)
        )

        return await cursor.fetchone()


# Получить все записи пользователя
async def get_user_bookings(user_id):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT service, date, time FROM bookings WHERE user_id=?",
            (user_id,)
        )

        return await cursor.fetchall()