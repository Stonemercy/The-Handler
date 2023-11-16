from aiosqlite import connect


# Used to move events from one database to another
async def migrate():
    async with connect("database.db") as db:
        all = await db.execute("Select * from events")
        records = await all.fetchall()
        async with connect("database2.db") as db2:
            for record in records:
                print(f"Migrating record {record[0]}")
                await db2.execute(
                    "Insert into events values (?, ?, ?, ?, ?, ?, ?)",
                    (
                        record[0],
                        record[1],
                        record[2],
                        record[3],
                        "False",
                        "False",
                        "False",
                    ),
                )
                await db2.commit()
                print("Done")
