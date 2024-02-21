from aiosqlite import connect
from datetime import datetime, timedelta
from helpers.functions import get_datetime
from helpers.classes import Embeds


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
        await db.execute(
            "CREATE TABLE IF NOT EXISTS dashboard(message_id, startup_time)"
        )
        await db.commit()


class Events:
    async def all():
        async with connect("data/database.db") as db:
            return await db.execute_fetchall("Select * from events order by date asc")

    async def specific(event_name: str):
        async with connect("data/database.db") as db:
            results = await db.execute_fetchall(
                "Select * from events where name is ?", (event_name,)
            )
            return False if results == [] else results[0]

    async def submit(
        date: str,
        time: str,
        name: str,
        submitter: int,
        description: str,
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
            record = await Events.specific(name)
            return record

    async def purge(date: datetime) -> None:
        """Purges events older than the date provided

        Parameters
        ---------
        date: `datetime`
            Events before this date are deleted
        """
        # probably need to add error handling for 0 events but w/e
        async with connect("data/database.db") as db:
            events = await Events.all()
            for i in events:
                time = get_datetime(" ".join([i[0], i[1]]))
                if time < date:
                    await db.execute("Delete from events where name = ?", (i[2],))
                    await db.commit()

    async def warnings(date: datetime) -> list:
        embeds = []
        async with connect("data/database.db") as db:
            all_events = await Events.all()
            if not all_events:
                return False
            for i in all_events:
                event_date = get_datetime(" ".join([i[0], i[1]]))
                if date < event_date < date + timedelta(days=1) and not eval(
                    str(i[5]).capitalize()
                ):
                    embed = Embeds.event_warning()
                    embed.title = i[0] + " " + i[1]
                    embed.description = f"# {i[2]}\n{i[3]}"
                    embeds.append(embed)
                    await db.execute(
                        "Update events set day_warn = 'true', week_warn = 'true' where name = ?",
                        (i[2],),
                    )
                    await db.commit()
                    continue
                elif date < event_date < date + timedelta(weeks=1) and not eval(
                    str(i[6]).capitalize()
                ):
                    embed = Embeds.event_warning()
                    embed.title = i[0] + " " + i[1]
                    embed.description = f"# {i[2]}\n{i[3]}"
                    embeds.append(embed)
                    await db.execute(
                        "Update events set week_warn = 'true' where name = ?",
                        (i[2],),
                    )
                    await db.commit()
                    continue
            return embeds if embeds != [] else False

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
    async def all():
        """Returns an iterable with every Row in the database"""
        async with connect("data/database.db") as db:
            return await db.execute_fetchall("Select * from gas order by date asc")

    async def years():
        """Returns a list of years with reports"""
        async with connect("data/database.db") as db:
            results = []
            records = await Gas.all()
            for i in records:
                year = str(get_datetime(i[0]).year)
                if year not in results:
                    results.append(year)
            return results

    async def yearly_spend(year: int):
        """This function gets the total spend for the provided year

        Parameters
        ---------
        year (int): The year to check

        Returns
        ---------
        `int` | `False`
        """
        total = 0
        async with connect("data/database.db") as db:
            all = await Gas.all()
            if all == []:
                return False
            for i in all:
                dt_obj = get_datetime(i[0])
                if dt_obj.year == year:
                    total += int(i[1])
                continue
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
                "Insert or ignore into gas values(?, ?)", (date, amount)
            )
            await db.commit()
            return True if reported is not None else False

    async def delete(date: datetime):
        async with connect("data/database.db") as db:
            all_items = await db.execute_fetchall("Select * from gas")
            if all_items == []:
                return False
            for i in all_items:
                if (
                    get_datetime(i[0]).replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    == date
                ):
                    await db.execute("Delete from gas where date = ?", (i[0],))
                    await db.commit()
                    return True
                else:
                    continue


class Electricity:
    async def all():
        """Returns an iterable with every Row in the database"""
        async with connect("data/database.db") as db:
            return await db.execute_fetchall(
                "Select * from electricity order by date asc"
            )

    async def years():
        """Returns a list of years with reports"""
        results = []
        records = await Electricity.all()
        for i in records:
            year = str(get_datetime(i[0]).year)
            if year not in results:
                results.append(year)
        return results

    async def yearly_spend(year: int):
        """This function gets the total spend for the provided year

        Parameters
        ---------
        year (int): The year to check

        Returns
        ---------
        `int` | `False`
        """
        total = 0
        async with connect("data/database.db") as db:
            all = await Electricity.all()
            if all == []:
                return False
            for i in all:
                dt_obj = get_datetime(i[0])
                if dt_obj.year == year:
                    total += int(i[1])
                continue

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
            all_items = await db.execute_fetchall("Select * from electricity")
            if all_items == []:
                return False
            for i in all_items:
                if get_datetime(i[0]) and get_datetime(i[0]) == date:
                    await db.execute("Delete from electricity where date = ?", (i[0],))
                    await db.commit()
                    return True
                else:
                    continue


class YouTube:
    async def current_id() -> str:
        async with connect("data/database.db") as db:
            all = await db.execute_fetchall("Select * from youtube")
            if all != []:
                return all[0][0]
            else:
                return False

    async def new_code(code: str):
        async with connect("data/database.db") as db:
            await db.execute("Delete from youtube")
            await db.execute("Insert into youtube values(?)", (code,))
            await db.commit()


class Dashboard:
    async def set_startup(startup_unix: int):
        async with connect("data/database.db") as db:
            data = await Dashboard.get_data()
            if not data:
                await db.execute("Insert into dashboard values (0, ?)", (startup_unix,))
                await db.commit()
            else:
                await db.execute(
                    "Update dashboard set startup_time = ? where message_id = ?",
                    (startup_unix, data[0]),
                )
                await db.commit()

    async def set_message_id(message_id):
        async with connect("data/database.db") as db:
            info = await Dashboard.get_data()
            if not info:
                return info
            await db.execute(
                "Update dashboard set message_id = ? where startup_time = ?",
                (message_id, info[1]),
            )
            await db.commit()

    async def get_data():
        async with connect("data/database.db") as db:
            info = await db.execute_fetchall("Select * from dashboard")
            return info[0] if info != [] else False
