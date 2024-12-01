from aiogram import executor

from loader import dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # await db.create()  # Initialize the database connection
    #
    # # Create necessary tables
    # await db.create_table_user_credentials()  # Correct table name
    # await db.create_table_group_credentials()
    # await db.create_table_gross_sheet()
    # await db.create_table_allowed_users()
    # await db.create_table_pwd_credentials()
    # await db.create_table_access_logs()

    # Set default commands
    await set_default_commands(dispatcher)

    # Notify admins
    await on_startup_notify(dispatcher)



if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)