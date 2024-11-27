from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
<<<<<<< HEAD
    text = ("Buyruqlar: ",
            "/start - Botni ishga tushirish",
            "/help - Yordam")
    
    await message.answer("\n".join(text))
=======
    text = ("Commands: ",
            "/start - to start bot",
            "/help - help info")
    
    await message.answer("\n".join(text))

>>>>>>> master
