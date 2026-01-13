import aiosqlite

async def init_db():
    async with aiosqlite.connect("database.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            rating INTEGER DEFAULT 0,
            is_premium INTEGER DEFAULT 0
        )
        """)
        await db.commit()
