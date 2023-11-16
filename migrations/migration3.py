from aiosqlite import connect


# used to move events from one database to another
async def migrate():
    async with connect("database_old.db") as db_old:
        # sending over events in the new format (missing hour-warnings)
        events = await db_old.execute("Select * from events")
        all_events = await events.fetchall()
        async with connect("database.db") as db_new:
            for record in all_events:
                print(f"Migrating record {record[0]}")
                await db_new.execute(
                    "Insert into events values (?, ?, ?, ?, ?, ?)",
                    (
                        record[0],
                        record[1],
                        record[2],
                        record[3],
                        record[5],
                        record[6],
                    ),
                )
                print("Done")
            await db_new.commit()

        # sending over youtube link
        youtube = await db_old.execute("Select * from youtube")
        link = await youtube.fetchone()
        async with connect("database.db") as db_new:
            await db_new.execute("Insert into youtube values (?)", (link))
            await db_new.commit()
