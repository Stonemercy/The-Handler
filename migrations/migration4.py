from aiosqlite import connect
from helpers.functions import get_datetime


# used to move events from one database to another
async def migrate():
    async with connect("data/database_old.db") as db_old:
        # sending over events in the new format (splitting date and time)
        all_events = await db_old.execute_fetchall("Select * from events")
        async with connect("data/database.db") as db_new:
            for record in all_events:
                print(f"Migrating record {record[1]}")
                dt_full = get_datetime(record[0])
                await db_new.execute(
                    "Insert into events values (?, ?, ?, ?, ?, ?, ?)",
                    (
                        dt_full.strftime("%d/%m/%Y"),
                        dt_full.strftime("%H:%M"),
                        record[1],
                        record[2],
                        record[3],
                        record[4],
                        record[5],
                    ),
                )
                print("Done")
            await db_new.commit()

        # sending over youtube link
        youtube = await db_old.execute("Select * from youtube")
        youtube = await youtube.fetchone()
        async with connect("data/database.db") as db_new:
            await db_new.execute("Insert into youtube values (?)", (youtube[0],))
            await db_new.commit()

        # sending over elecy data
        elecy = await db_old.execute_fetchall("Select * from electricity")
        async with connect("data/database.db") as db_new:
            for i in elecy:
                await db_new.execute(
                    "Insert into electricity values (?, ?)", (i[0], i[1])
                )
            await db_new.commit()

        # sending over gas data
        gas = await db_old.execute_fetchall("Select * from gas")
        async with connect("data/database.db") as db_new:
            for i in elecy:
                await db_new.execute("Insert into gas values (?, ?)", (i[0], i[1]))
            await db_new.commit()
