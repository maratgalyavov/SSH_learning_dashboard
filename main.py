import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.dispatcher.router import Router

import asyncio

from functions.handlers import setup_handlers
from functions.save_load_data import save_connection_details, load_connection_details

from config import API_TOKEN

saved_connection_details = load_connection_details()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
router = Router()

setup_handlers(router)

dispatcher = Dispatcher()
dispatcher.include_router(router)

if __name__ == '__main__':
    asyncio.run(dispatcher.start_polling(bot))