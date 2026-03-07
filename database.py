import aiosqlite

DB = "booking.db"


# ---------- INIT DATABASE ----------

async def init_db():
    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS bookings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            service TEXT,
            date TEXT,
            time TEXT,
            status TEXT
        )
        """)

        await db.commit()


# ---------- ADD BOOKING (pending) ----------

async def add_booking(user_id, name, service, date, time):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            """
            INSERT INTO bookings (user_id, name, service, date, time, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
            """,
            (user_id, name, service, date, time)
        )

        await db.commit()

        return cursor.lastrowid


# ---------- APPROVE BOOKING ----------

async def approve_booking_db(booking_id):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT user_id, service, date, time FROM bookings WHERE id=?",
            (booking_id,)
        )

        booking = await cursor.fetchone()

        if not booking:
            return None

        await db.execute(
            "UPDATE bookings SET status='approved' WHERE id=?",
            (booking_id,)
        )

        await db.commit()

        return booking


# ---------- REJECT BOOKING ----------

async def reject_booking_db(booking_id):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT user_id, service, date, time FROM bookings WHERE id=?",
            (booking_id,)
        )

        booking = await cursor.fetchone()

        if not booking:
            return None

        await db.execute(
            "UPDATE bookings SET status='rejected' WHERE id=?",
            (booking_id,)
        )

        await db.commit()

        return booking


# ---------- GET ALL BOOKINGS (admin) ----------

async def get_bookings():

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute("SELECT * FROM bookings")

        return await cursor.fetchall()


# ---------- DELETE BOOKING ----------

async def delete_booking(book_id):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "DELETE FROM bookings WHERE id=?",
            (book_id,)
        )

        await db.commit()


# ---------- BUSY TIMES (only approved) ----------

async def get_busy_times(date):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            "SELECT time FROM bookings WHERE date=? AND status='approved'",
            (date,)
        )

        rows = await cursor.fetchall()

        return [r[0] for r in rows]


# ---------- USER BOOKING CHECK ----------

async def get_user_booking(user_id, service):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            """
            SELECT date, time
            FROM bookings
            WHERE user_id=? AND service=? AND status='approved'
            """,
            (user_id, service)
        )

        return await cursor.fetchone()


# ---------- USER BOOKINGS ----------

async def get_user_bookings(user_id):

    async with aiosqlite.connect(DB) as db:

        cursor = await db.execute(
            """
            SELECT service, date, time
            FROM bookings
            WHERE user_id=? AND status='approved'
            """,
            (user_id,)
        )

        return await cursor.fetchall()