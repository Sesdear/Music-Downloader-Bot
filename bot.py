import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


from config import TOKEN
from handlers import *

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(message_handler_router)




    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
