from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy

from middlewares.logger import LoggerMiddleware

from handlers.registration import router as registration_router
from handlers.user import router as user_router
from handlers.admin import router as admin_router
from handlers.schedule import router as schedule_router

from configs.loader import loadConfig
from configs.database import init_db, close_db

import asyncio

config = loadConfig()
storage = MemoryStorage()

bot = Bot(config["telegram"]["token"])
dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.GLOBAL_USER)

dp.message.middleware(LoggerMiddleware())
dp.callback_query.middleware(LoggerMiddleware())

dp.include_routers(
    registration_router, 
    user_router, 
    admin_router,
    schedule_router
)

async def main():
    db = await init_db()

    await db.execute(
        """
            INSERT INTO users(id, name, surname, grade_id, is_admin) VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET is_admin = excluded.is_admin
        """,
        (config["telegram"]["admin_id"], "Администратор", "Администратор", 1, 1,),
    )
    await db.commit()
    
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())