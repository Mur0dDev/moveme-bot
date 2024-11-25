import asyncio
from utils.db_api.postgresql import Database
from asyncpg.exceptions import UniqueViolationError


async def test():
    db = Database()
    await db.create()
    print("Creating the Users table...")

    # Drop the table if you want a clean start (comment out in production)
    # await db.drop_users()

    await db.create_table_users()
    print("Table created successfully.")

    print("Adding users to the database...")

    users_to_add = [
        ("anvar", "sariqdev", 123456789),
        ("olim", "olim223", 12341123),
        ("1", "1", 131231),
        ("1", "1", 23324234),
        ("John", "JohnDoe", 4388229)
    ]

    for full_name, username, telegram_id in users_to_add:
        try:
            user = await db.add_user(full_name, username, telegram_id)
            if user:
                print(f"User added: {user}")
            else:
                print(f"User with telegram_id {telegram_id} already exists.")
        except UniqueViolationError:
            print(f"User with telegram_id {telegram_id} already exists.")
        except Exception as e:
            print(f"Error adding user with telegram_id {telegram_id}: {e}")

    print("Users added successfully.")

    print("Fetching all users...")
    users = await db.select_all_users()
    print(f"All users: {users}")

    print("Fetching a specific user with ID 5...")
    user = await db.select_user(id=5)
    if user:
        print(f"User found: {user}")
    else:
        print("User with ID 5 not found.")


# Workaround for asyncio.run() issues on Windows
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test())
