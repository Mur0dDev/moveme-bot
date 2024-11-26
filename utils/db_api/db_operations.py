from utils.db_api.postgresql import Database

db = Database()

async def get_all_user_credentials():
    """
    Fetch all user credentials from the database.

    Returns:
        list: A list of rows containing user credentials.
    """
    sql = "SELECT * FROM user_credentials;"
    return await db.execute(sql, fetch=True)
