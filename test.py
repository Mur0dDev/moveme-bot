from utils.db_api.postgresql import Database
import asyncio
from datetime import datetime

async def test_database():
    db = Database()
    await db.create()  # Initialize the database connection

    # Test table creation
    print("Creating tables...")
    await db.create_table_user_credentials()
    await db.create_table_group_credentials()
    await db.create_table_gross_sheet()
    await db.create_table_allowed_users()
    await db.create_table_pwd_credentials()
    await db.create_table_access_logs()
    print("All tables created successfully!")

    # Test inserting data into user_credentials
    print("Inserting data into user_credentials...")
    await db.add_user_credential(
        telegram_id=123456789,
        full_name="John Doe",
        dob=datetime.strptime("1990-01-01", "%Y-%m-%d").date(),  # Convert to a date object
        phone_number="+1234567890",
        role="Dispatcher"
    )
    print("Inserted user credentials successfully!")

    # Test selecting data from user_credentials
    print("Selecting data from user_credentials...")
    users = await db.select_all_user_credentials()
    print("User Credentials:", users)

    # Test updating data in user_credentials
    print("Updating user credentials...")
    await db.update_user_credential(telegram_id=123456789, full_name="John Updated")
    updated_user = await db.select_user_credential(telegram_id=123456789)
    print("Updated User Credential:", updated_user)

    # Close the database pool
    await db.pool.close()
    print("Database connection closed.")

# Run the test
asyncio.run(test_database())
