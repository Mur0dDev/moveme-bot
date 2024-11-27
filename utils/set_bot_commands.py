from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "start"),
<<<<<<< HEAD
=======
            types.BotCommand("pwd", "passwords"),
            types.BotCommand("settings", "settings"),
            types.BotCommand("about", "about this bot"),
>>>>>>> master
        ]
    )
