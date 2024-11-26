import asyncio
from aiogram import types
from aiogram.dispatcher import Dispatcher
from loader import dp
from filters import IsPrivate, IsSuperAdmin
from test import read_all_user_credentials

@dp.message_handler(IsPrivate(), IsSuperAdmin(), commands=['start', 'help'])
async def start(message: types.Message):
    await message.answer(f"You are super admin")
    await read_all_user_credentials()


