import asyncio
import asyncpg
from data import config

async def test_connection():
    try:
        conn = await asyncpg.connect(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )
        print("Database connection successful.")
        await conn.close()
    except Exception as e:
        print(f"Failed to connect to the database: {e}")

asyncio.run(test_connection())
