from aiogram import executor

from loader import dp, db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
<<<<<<< HEAD
    await db.create()
    # await db.drop_users()
    await db.create_table_users()

    await set_default_commands(dispatcher)

=======
    try:
        # Initialize the database connection
        await db.create()
        print("Database connection pool initialized.")
    except Exception as e:
        print(f"Error initializing database connection pool: {e}")

    # Create all required tables
    await db.create_table_user_credentials()
    await db.create_table_group_credentials()
    await db.create_table_gross_sheet()
    await db.create_table_allowed_users()
    await db.create_table_pwd_credentials()
    await db.create_table_access_logs()

    # Set default bot commands (/start and /help)
    await set_default_commands(dispatcher)

    # Notify admins about the bot startup
>>>>>>> master
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
