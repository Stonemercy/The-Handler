from aiosqlite import connect
from datetime import datetime, timedelta

from requests import delete
from helpers.generators import Embeds


async def db_startup():
    async with connect("data/database.db") as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS events(date timestamp, name text, description text, submitter, day_warn default 'false', week_warn default 'false')"
        )
        await db.execute("CREATE TABLE IF NOT EXISTS youtube(video_id text)")
        await db.execute(
            "CREATE TABLE IF NOT EXISTS electricity(date timestamp, amount)"
        )
        await db.execute("CREATE TABLE IF NOT EXISTS gas(date timestamp, amount)")
        await db.execute("CREATE TABLE IF NOT EXISTS boke(date timestamp)")
        await db.execute(
            "CREATE TABLE IF NOT EXISTS mhnow(start_time timestamp, end_time timestamp, event_name, event_desc)"
        )
        await db.commit()


class Events:
    async def all():
        async with connect("data/database.db") as db:
            return await db.execute_fetchall("Select * from events order by date asc")

    async def specific(
        event_name: str = None,
        event_date: datetime = None,
    ):
        if event_name is not None:
            async with connect("data/database.db") as db:
                async with db.execute(
                    "Select * from events where name is ?", (event_name,)
                ) as cursor:
                    result = await cursor.fetchone()
                    if result is not None:
                        return result
                    else:
                        return None
        if event_date is not None:
            async with connect("data/database.db") as db:
                async with db.execute(
                    "Select * from events where date is ?", (event_date,)
                ) as cursor:
                    result = await cursor.fetchone()
                    if result is not None:
                        return result
                    else:
                        return None

    async def submit(
        date_and_time: datetime,
        name: str,
        submitter: int,
        description: str = "No description",
    ):
        async with connect("data/database.db") as db:
            await db.execute(
                "Insert or ignore into events values (?, ?, ?, ?, ?, ?)",
                (
                    date_and_time,
                    name,
                    description,
                    submitter,
                    "false",
                    "false",
                ),
            )
            await db.commit()

    async def purge():
        now = datetime.now()
        async with connect("data/database.db") as db:
            async with db.execute_fetchall("Select * from events") as events:
                for event in events:
                    time_from_iso = datetime.fromisoformat(event[0])
                    if time_from_iso < now:
                        await db.execute(
                            "Delete from events where date = ?", (event[0],)
                        )
                        await db.commit()

    async def warnings(channel):
        now = datetime.now()
        warnings = False
        embeds = []
        async with connect("data/database.db") as db:
            all_events = await Events.all()
            if all_events == []:
                return False
            for event in all_events:
                unit = None
                time_from_iso = datetime.fromisoformat(event[0])
                if (
                    now < time_from_iso < now + timedelta(days=1)
                    and event[4] == "false"
                ):
                    await db.execute(
                        "Update events set day_warn = 'true', week_warn = 'true' where date = ?",
                        (event[0],),
                    )
                    await db.commit()
                    unit = "day"
                    warnings = True
                elif (
                    now < time_from_iso < now + timedelta(weeks=1)
                    and event[5] == "false"
                ):
                    await db.execute(
                        "Update events set week_warn = 'true' where date = ?",
                        (event[0],),
                    )
                    await db.commit()
                    unit = "week"
                    warnings = True

                if unit is None:
                    continue
                embed = Embeds.event_warning()
                embed.title = datetime.fromisoformat(event[0]).strftime("%d/%m/%y")
                embed.description = f"{event[1]}\n{event[2]}"
                embeds.append(embed)

            if warnings:
                return embeds
            else:
                return False

    async def delete(event):
        async with connect("data/database.db") as db:
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
        async with connect("data/database.db") as db:
            all = await db.execute("Select * from gas")
            latest = await all.fetchmany(18)
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

    async def report(amount: float | int, date: datetime = datetime.now()):
        async with connect("data/database.db") as db:
            await db.execute("Insert or ignore into gas values(?, ?)", (date, amount))
            await db.commit()
            check = await db.execute("Select * from gas where date = ?", (date,))
            found = await check.fetchone()
            if found is not None:
                return True
            else:
                return False

    async def delete(date: str):
        async with connect("data/database.db") as db:
            grab = await db.execute("Select * from gas")
            fetch = await grab.fetchmany(18)
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
        async with connect("data/database.db") as db:
            all = await db.execute("Select * from electricity")
            latest = await all.fetchmany(18)
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

    async def report(amount: float | int, date: datetime = datetime.now()):
        async with connect("data/database.db") as db:
            await db.execute(
                "Insert or ignore into electricity values(?, ?)", (date, amount)
            )
            await db.commit()
            check = await db.execute(
                "Select * from electricity where date = ?", (date,)
            )
            found = await check.fetchone()
            if found is not None:
                return True
            else:
                return False

    async def delete(date: str):
        async with connect("data/database.db") as db:
            grab = await db.execute("Select * from electricity")
            fetch = await grab.fetchmany(18)
            for i in fetch:
                if datetime.fromisoformat(i[0]).strftime("%d/%m/%y") == date:
                    await db.execute("Delete from electricity where date = ?", (i[0],))
                    await db.commit()
                    return True
                else:
                    continue
            return False


class YouTube:
    async def current_id() -> str:
        async with connect("data/database.db") as db:
            all = await db.execute("Select * from youtube")
            current_id = await all.fetchone()
            current_id = current_id[0]
            if current_id is not None:
                return current_id
            else:
                return False

    async def new_code(code: str):
        async with connect("data/database.db") as db:
            await db.execute("Delete from youtube")
            await db.execute("Insert into youtube values(?)", (code,))
            await db.commit()


class Pearl:
    async def boked():
        now = datetime.now()
        async with connect("data/database.db") as db:
            await db.execute("Insert into boke values(?)", (now,))
            await db.commit()

    async def didnt_boke(date: str) -> bool:
        async with connect("data/database.db") as db:
            grab = await db.execute("Select * from boke")
            fetch = await grab.fetchmany(18)
            if fetch != []:
                for i in fetch:
                    if datetime.fromisoformat(i[0]).strftime("%d/%m/%y") == date:
                        await db.execute("Delete from boke where date = ?", (i[0],))
                        await db.commit()
                        return True
                    else:
                        continue
            else:
                return False

    async def all_bokes():
        async with connect("data/database.db") as db:
            select = await db.execute("Select * from boke order by date asc")
            all = await select.fetchall()
            if all:
                return all
            else:
                return False


class MHNow:
    async def all():
        async with connect("data/database.db") as db:
            all = await db.execute_fetchall(
                "Select * from mhnow order by start_time asc"
            )
            return all if all else False

    async def new_event(
        start_time: datetime, end_time: datetime, event_name: str, event_desc: str
    ):
        async with connect("data/database.db") as db:
            await db.execute(
                "Insert into mhnow values (?, ?, ?, ?)",
                (start_time, end_time, event_name, event_desc),
            )
            await db.commit()
            check_search = await db.execute(
                "Select * from mhnow where event_name = ?", (event_name,)
            )
            check_result = await check_search.fetchone()
            return check_result if check_result else False

    async def delete_event(event_name: str):
        async with connect("data/database.db") as db:
            await db.execute("Delete from mhnow where event_name = ?", (event_name,))
            await db.commit()
            check = await db.execute(
                "Select * from mhnow where event_name = ?", (event_name,)
            )
            result = await check.fetchone()
            return True if result is None else False

    async def delete_old():
        deleted_list = []
        async with connect("data/database.db") as db:
            now = datetime.now()
            events = await db.execute_fetchall("Select * from mhnow")
            for i in events:
                event_time = datetime.fromisoformat(i[1])
                if event_time < now:
                    await db.execute("Delete from mhnow where event_name = ?", (i[2],))
                    await db.commit()
                    deleted_list.append(i[2])
                    continue
            return deleted_list if len(deleted_list) > 0 else False
