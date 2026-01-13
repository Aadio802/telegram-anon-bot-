import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN
from database import init_db
import aiosqlite

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

waiting_users = []
chats = {}
SPAM = ["http", "www", "t.me", "crypto", "casino", "bet"]

async def get_premium(uid):
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("SELECT is_premium FROM users WHERE user_id=?", (uid,)) as cur:
            row = await cur.fetchone()
            if row:
                return row[0]
        await db.execute("INSERT INTO users (user_id) VALUES (?)", (uid,))
        await db.commit()
        return 0

@dp.message(Command("start"))
async def start(msg):
    await msg.answer("Welcome. Type /find to match.")

@dp.message(Command("find"))
async def find(msg):
    uid = msg.from_user.id
    if uid in chats or uid in waiting_users:
        return

    if waiting_users:
        other = waiting_users.pop(0)
        chats[uid] = other
        chats[other] = uid
        await bot.send_message(uid, "Connected.")
        await bot.send_message(other, "Connected.")
    else:
        waiting_users.append(uid)
        await msg.answer("Searching...")

@dp.message()
async def relay(msg):
    uid = msg.from_user.id
    if uid not in chats:
        return

    premium = await get_premium(uid)
    if not premium:
        for w in SPAM:
            if w in (msg.text or "").lower():
                await msg.answer("Links are for premium users.")
                return

    await bot.copy_message(chats[uid], msg.chat.id, msg.message_id)

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
