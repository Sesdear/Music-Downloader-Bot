from aiogram.types import Message
from aiogram import Router

from downloaders import compas

router = Router()

@router.message()
async def message_handler(message: Message):
    await compas(message=message)