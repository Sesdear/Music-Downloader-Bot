from aiogram.types import Message
from aiogram import Router
from aiogram.filters import Command
from messages_config import START_MESSAGE

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(START_MESSAGE)