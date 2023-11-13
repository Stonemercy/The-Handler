from aiosqlite import connect
from datetime import datetime, timedelta


async def db_startup():
    async with connect("database.db") as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS events(date_and_time timestamp, name text unique, description text, submitter, one_hour_warn default 'false', one_day_warn default 'false', one_week_warn default 'false')"
        )
        await db.execute("CREATE TABLE IF NOT EXISTS youtube(video_id)")
        await db.execute("CREATE TABLE IF NOT EXISTS electricity(date, amount)")
        await db.execute("CREATE TABLE IF NOT EXISTS gas(date, amount)")
        await db.commit()
        print("Database has been setup")


class Events:
    async def all():
        async with connect("database.db") as db:
            return await db.execute_fetchall("Select * from events")

    async def specific(event_name: str):
        async with connect("database.db") as db:
            async with db.execute(
                "Select * from events where name is ?", (event_name,)
            ) as cursor:
                result = await cursor.fetchone()
                return result

    async def submit(
        date_and_time: datetime,
        name: str,
        submitter: int,
        description: str = "No description",
    ):
        async with connect("database.db") as db:
            await db.execute(
                "Insert or ignore into events values (?, ?, ?, ?, ?, ?, ?)",
                (
                    date_and_time,
                    name,
                    description,
                    submitter,
                    "false",
                    "false",
                    "false",
                ),
            )
            await db.commit()

    async def purge():
        now = datetime.now()
        one_month_ago = now - timedelta(weeks=4)
        async with connect("database.db") as db:
            async with db.execute_fetchall("Select * from events") as events:
                for event in events:
                    time_from_iso = datetime.fromisoformat(event[0])
                    if one_month_ago < time_from_iso < now:
                        await db.execute(
                            "Delete from events where date_and_time = ?", (event[0],)
                        )
                        await db.commit()

    async def warnings(event):
        now = datetime.now()
        time_from_iso = datetime.fromisoformat(event[0])
        async with connect("database.db") as db:
            if now < time_from_iso < now + timedelta(hours=1) and event[4] == "false":
                await db.execute(
                    "Update events set one_hour_warn = 'true', one_day_warn = 'true', one_week_warn = 'true' where date_and_time = ?",
                    (event[0],),
                )
                await db.commit()
                return "hour"

            if now < time_from_iso < now + timedelta(days=1) and event[5] == "false":
                await db.execute(
                    "Update events set one_day_warn = 'true', one_week_warn = 'true' where date_and_time = ?",
                    (event[0],),
                )
                await db.commit()
                return "day"

            if now < time_from_iso < now + timedelta(weeks=1) and event[6] == "false":
                await db.execute(
                    "Update events set one_week_warn = 'true' where date_and_time = ?",
                    (event[0],),
                )
                await db.commit()
                return "week"

    async def delete(event):
        async with connect("database.db") as db:
            async with db.execute(
                "Select * from events where name = ?", (event,)
            ) as cur:
                first = await cur.fetchone()
                if first is None:
                    return False
                else:
                    pass
            await db.execute("Delete from events where name = ?", (event,))
            await db.commit()

            async with db.execute(
                "Select * from events where name = ?", (event,)
            ) as cur:
                first = await cur.fetchone()
                if first is None:
                    return True
                else:
                    return False


class Gas:
    async def yearly_average():
        now = datetime.now()
        year = now - timedelta(weeks=52)
        total = 0
        async with connect("database.db") as db:
            all = await db.execute("Select * from gas")
            latest = await all.fetchmany(12)
            if latest == []:
                return False
            for i in latest:
                iso = datetime.fromisoformat(i[0])
                if year < iso < now:
                    total += float(i[1])
                    continue
                else:
                    continue
            return round(total, 2)

    async def report(amount: float | int):
        now = datetime.now()
        async with connect("database.db") as db:
            await db.execute("Insert or ignore into gas values(?, ?)", (now, amount))
            await db.commit()
            check = await db.execute("Select * from gas where date = ?", (now,))
            found = await check.fetchone()
            if found is not None:
                return True
            else:
                return False

    async def delete(date: str):
        async with connect("database.db") as db:
            grab = await db.execute("Select * from gas")
            fetch = await grab.fetchmany(12)
            for i in fetch:
                if datetime.fromisoformat(i[0]).strftime("%d/%m/%y") == date:
                    await db.execute("Delete from gas where date = ?", (i[0],))
                    await db.commit()
                    return True
                else:
                    continue
            return False


class Electricity:
    async def yearly_average():
        now = datetime.now()
        year = now - timedelta(weeks=52)
        total = 0
        async with connect("database.db") as db:
            all = await db.execute("Select * from electricity")
            latest = await all.fetchmany(12)
            if latest == []:
                return False
            for i in latest:
                iso = datetime.fromisoformat(i[0])
                if year < iso < now:
                    total += float(i[1])
                    continue
                else:
                    continue
            return round(total, 2)

    async def report(amount: float | int):
        now = datetime.now()
        async with connect("database.db") as db:
            await db.execute(
                "Insert or ignore into electricity values(?, ?)", (now, amount)
            )
            await db.commit()
            check = await db.execute("Select * from electricity where date = ?", (now,))
            found = await check.fetchone()
            if found is not None:
                return True
            else:
                return False

    async def delete(date: str):
        async with connect("database.db") as db:
            grab = await db.execute("Select * from electricity")
            fetch = await grab.fetchmany(12)
            for i in fetch:
                if datetime.fromisoformat(i[0]).strftime("%d/%m/%y") == date:
                    await db.execute("Delete from electricity where date = ?", (i[0],))
                    await db.commit()
                    return True
                else:
                    continue
            return False


class YouTube:
    async def current_id():
        async with connect("database.db") as db:
            all = await db.execute("Select * from youtube")
            current_id = await all.fetchone()
            if current_id is not None:
                return current_id
            else:
                return False

    async def new_code(code: str):
        async with connect("database.db") as db:
            await db.execute("Delete from youtube")
            await db.execute("Insert into youtube values(?)", (code,))
            await db.commit()
