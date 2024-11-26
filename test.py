import asyncio
from utils.db_api.db_operations import get_user_role_by_telegram_id
from utils.db_api.postgresql import Database

async def test_get_user_role_by_telegram_id():
    db = Database()

    # Initialize the database connection
    await db.create()
    print("Database initialized successfully!")

    # Test with an existing Telegram ID
    existing_telegram_id = 7262828142  # Replace with a valid Telegram ID from your database
    role = await get_user_role_by_telegram_id(existing_telegram_id)
    if role:
        print(f"Role for Telegram ID {existing_telegram_id}: {role}")
    else:
        print(f"Telegram ID {existing_telegram_id} does not exist in the user_credentials table.")

    # Test with a non-existing Telegram ID
    non_existing_id = 1234567890  # Replace with an invalid Telegram ID
    role = await get_user_role_by_telegram_id(non_existing_id)
    if role:
        print(f"Role for Telegram ID {non_existing_id}: {role}")
    else:
        print(f"Telegram ID {non_existing_id} does not exist in the user_credentials table.")

    # Close the database connection
    await db.pool.close()
    print("Database connection closed.")

# Run the test
asyncio.run(test_get_user_role_by_telegram_id())
