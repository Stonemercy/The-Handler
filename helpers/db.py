from aiosqlite import connect
from datetime import datetime, timedelta
from helpers.functions import get_datetime
from helpers.generators import Embeds


async def db_startup():
    async with connect("data/database.db") as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS events(date text, time text, name text, description text, submitter, day_warn default 'false', week_warn default 'false')"
        )
        await db.execute("CREATE TABLE IF NOT EXISTS youtube(video_id text)")
        await db.execute(
            "CREATE TABLE IF NOT EXISTS electricity(date timestamp, amount)"
        )
        await db.execute("CREATE TABLE IF NOT EXISTS gas(date timestamp, amount)")
        """ await db.execute("CREATE TABLE IF NOT EXISTS boke(date timestamp)")
        await db.execute(
            "CREATE TABLE IF NOT EXISTS mhnow(start_time timestamp, end_time timestamp, event_name, event_desc)"
        )"""
        await db.commit()


class Events:
    async def all():
        async with connect("data/database.db") as db:
            return await db.execute_fetchall("Select * from events order by date asc")

    async def specific(
        event_name: str,
    ):
        async with connect("data/database.db") as db:
            results = await db.execute_fetchall(
                "Select * from events where name is ?", (event_name,)
            )
            return results[0]

    async def submit(
        date: str,
        time: str,
        name: str,
        submitter: int,
        description: str = "No description",
    ):
        async with connect("data/database.db") as db:
            await db.execute(
                "Insert into events values (?, ?, ?, ?, ?, ?, ?)",
                (
                    date,
                    time,
                    name,
                    description,
                    submitter,
                    "false",
                    "false",
                ),
            )
            await db.commit()

    async def purge(now: datetime):
        async with connect("data/database.db") as db:
            events = await Events.all()
            for i in events:
                time = get_datetime(" ".join([i[0], i[1]]))
                if time < now:
                    await db.execute("Delete from events where name = ?", (i[2],))
                    await db.commit()

    async def warnings(now):
        embeds = []
        async with connect("data/database.db") as db:
            all_events = await Events.all()
            if not all_events:
                return False
            for i in all_events:
                event_date = datetime.combine(
                    get_datetime(i[0]).date(),
                    get_datetime(i[1]).time(),
                )
                if now < event_date < now + timedelta(days=1) and not bool(i[4]):
                    embed = Embeds.event_warning()
                    embed.title = i[0] + " " + i[1]
                    embed.description = f"# {i[2]}\n{i[3]}"
                    embeds.append(embed)
                    await db.execute(
                        "Update events set day_warn = 'true', week_warn = 'true' where name = ?",
                        (i[2],),
                    )
                    await db.commit()
                elif now < event_date < now + timedelta(weeks=1) and not bool(i[5]):
                    embed.title = i[0] + " " + i[1]
                    embed.description = f"# {i[2]}\n{i[3]}"
                    embeds.append(embed)
                    await db.execute(
                        "Update events set week_warn = 'true' where name = ?",
                        (i[2],),
                    )
                    await db.commit()
            return embeds if embeds else False

    async def delete(event):
        async with connect("data/database.db") as db:
            specific = await Events.specific(event)
            if not specific:
                return False
            await db.execute("Delete from events where name = ?", (event,))
            await db.commit()
            specific = await Events.specific(event)
            return False if specific else True


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
    """How to engage with the Electricity DB"""

    async def all():
        """Returns an iterable with every Row in the database"""
        async with connect("data/database.db") as db:
            return await db.execute_fetchall(
                "Select * from electricity order by date asc"
            )

    async def yearly_spend(year: int):
        """This function gets the total spend for the provided year

        Args:
            year (int): The year to check

        Returns:
            `int` | `False`
        """
        total = 0
        async with connect("data/database.db") as db:
            all = await Electricity.all()
            if not all:
                return False
            for i in all:
                dt_obj = get_datetime(i[0])
                if dt_obj.year == year:
                    total += int(i[1])
                    continue
                else:
                    return total
            return total

    async def report(amount: float | int, date: datetime) -> bool:
        """Insert a new payment into the database

        Parameters
        ----------
            amount: `float` | `int`
            date: `datetime`

        Returns
        ----------
            bool: True if it worked, False if it didn't
        """
        async with connect("data/database.db") as db:
            reported = await db.execute_insert(
                "Insert or ignore into electricity values(?, ?)", (date, amount)
            )
            await db.commit()
            return True if reported is not None else False

    async def delete(date: datetime):
        async with connect("data/database.db") as db:
            item_to_del = await db.execute_fetchall("Select * from electricity")
            if item_to_del == []:
                return False
            for i in item_to_del:
                if get_datetime(i[0]) and get_datetime(i[0]) == date:
                    await db.execute("Delete from electricity where date = ?", (i[0],))
                    await db.commit()
                    return True
                else:
                    continue


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


"""class Pearl:
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
                return False"""


"""class MHNow:
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
"""
