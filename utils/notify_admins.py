import logging
<<<<<<< HEAD

from aiogram import Dispatcher

=======
from aiogram import Dispatcher
>>>>>>> master
from data.config import ADMINS


async def on_startup_notify(dp: Dispatcher):
<<<<<<< HEAD
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "The bot has started")

        except Exception as err:
            logging.exception(err)
=======
    """
    Notify admins about the bot startup.
    """
    try:
        # Notify admins about the bot startup
        for admin in ADMINS:
            try:
                await dp.bot.send_message(admin, "MoveMeGroupBot has started successfully.")
            except Exception as err:
                logging.exception(f"Error notifying admin {admin}: {err}")

    except Exception as err:
        logging.exception(f"Error during bot startup notification: {err}")
>>>>>>> master
