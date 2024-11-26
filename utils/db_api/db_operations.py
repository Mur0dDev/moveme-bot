from loader import db

async def get_user_role_by_telegram_id(telegram_id: int):
    """
    Checks if a user exists in the user_credentials table by telegram_id.
    If the user exists, returns the user's role. Otherwise, returns False.

    Args:
        telegram_id (int): The Telegram ID of the user.

    Returns:
        str | bool: The user's role if the user exists, or False if not.
    """
    sql = """
    SELECT role FROM user_credentials
    WHERE telegram_id = $1;
    """
    role = await db.execute(sql, telegram_id, fetchval=True)
    return role if role else False
