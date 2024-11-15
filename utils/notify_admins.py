import logging
from aiogram import Dispatcher
from data.config import ADMINS
from sheet.google_sheets_integration import update_cache  # Import the cache update function


async def on_startup_notify(dp: Dispatcher):
    try:
        # Step 1: Update the cache
        update_cache()  # Direct call since aiogram 2.14 doesn't require async for this function
        logging.info("Cache updated successfully on bot startup.")

        # Step 2: Notify admins about the bot startup
        for admin in ADMINS:
            try:
                await dp.bot.send_message(admin, "MoveMeGroupBot has started and cache is updated.")
            except Exception as err:
                logging.exception(f"Error notifying admin {admin}: {err}")

    except Exception as err:
        logging.exception(f"Error during bot startup: {err}")
