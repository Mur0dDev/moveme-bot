import asyncio
from utils.db_api.postgresql import Database


async def read_all_user_credentials():
    db = Database()  # Create an instance of the Database class
    await db.create()  # Initialize the database connection pool

    # SQL query to fetch all data from the user_credentials table
    sql = "SELECT * FROM user_credentials;"

    print("Fetching all data from user_credentials...")
    data = await db.execute(sql, fetch=True)  # Fetch all rows
    for row in data:
        print(row)  # Print each row

    await db.pool.close()  # Close the database connection pool
    print("Database connection closed.")


if __name__ == "__main__":
    asyncio.run(read_all_user_credentials())
