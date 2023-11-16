from aiosqlite import connect
from datetime import datetime


# Used to move events from one database to another
async def migrate():
    async with connect("database_old.db") as db_old:
        all = await db_old.execute("Select * from events")
        records = await all.fetchall()
        async with connect("database.db") as db_new:
            for record in records:
                print(f"Migrating record {record[0]}")
                await db_new.execute(
                    "Insert into events values (?, ?, ?, ?, ?, ?, ?)",
                    (
                        datetime.fromisoformat(record[0]).strftime("%d/%m/%y"),
                        record[1],
                        record[2],
                        record[3],
                        "False",
                        "False",
                        "False",
                    ),
                )
                print("Done")
            await db_new.commit()


# remember to do the other tables next time
