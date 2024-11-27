import logging
from datetime import datetime
from utils.db_api.postgresql import Database

db = Database()


async def add_user_to_database(user_data):
    """
    Inserts a new user into the 'user_credentials' table in PostgreSQL.

    Args:
        user_data (dict): A dictionary containing the user's data:
            - "user_id" (int): Telegram ID of the user.
            - "full_name" (str): Full name of the user.
            - "date_of_birth" (str or datetime.date): Date of birth in 'YYYY-MM-DD' format.
            - "phone" (str): User's phone number.
            - "role" (str): User's role (e.g., "Dispatcher").
    """
    try:
        # Ensure the date is converted to a valid format for PostgreSQL
        dob = user_data["date_of_birth"]
        if isinstance(dob, str):
            dob = datetime.strptime(dob, "%Y-%m-%d").date()

        print(f"Adding user {user_data['user_id']} to PostgreSQL...")
        await db.add_user_credential(
            telegram_id=user_data["user_id"],
            full_name=user_data["full_name"],
            dob=dob,
            phone_number=user_data["phone"],
            role=user_data["role"],
        )
        print("User added successfully.")
    except Exception as e:
        logging.exception(f"Failed to add user to PostgreSQL: {e}")
        raise

async def add_group_to_database(group_data):
    """
    Inserts a new group into the 'group_credentials' table in PostgreSQL.

    Args:
        group_data (dict): A dictionary containing the group's data:
            - "group_id" (int): ID of the group.
            - "company_name" (str): Name of the company.
            - "group_name" (str): Title of the group.
            - "group_type" (str): Type of the group (e.g., "drivers").
            - "truck_number" (str): Associated truck number.
            - "driver_name" (str): Name of the driver.
    """
    try:
        sql = """
        INSERT INTO group_credentials (group_id, company_name, group_name, group_type, truck_number, driver_name)
        VALUES ($1, $2, $3, $4, $5, $6)
        """
        await db.execute(
            sql,
            group_data["group_id"],
            group_data["company_name"],
            group_data["group_name"],
            group_data["group_type"],
            group_data["truck_number"],
            group_data["driver_name"],
            execute=True
        )
        print("Group successfully added to the database.")
    except Exception as e:
        logging.exception(f"Error adding group to the database: {e}")
        raise

async def get_user_role_by_telegram_id(telegram_id):
    """
    Fetches the user's role from the 'user_credentials' table in PostgreSQL.

    Args:
        telegram_id (int): Telegram ID of the user.

    Returns:
        str: Role of the user (e.g., "Dispatcher", "Safety").
    """
    sql = "SELECT role FROM user_credentials WHERE telegram_id = $1"
    role = await db.execute(sql, telegram_id, fetchval=True)
    return role

async def get_full_name_by_user_id(telegram_id):
    """
    Fetches the user's full name from the 'user_credentials' table in PostgreSQL.

    Args:
        telegram_id (int): Telegram ID of the user.

    Returns:
        str: Full name of the user.
    """
    sql = "SELECT full_name FROM user_credentials WHERE telegram_id = $1"
    full_name = await db.execute(sql, telegram_id, fetchval=True)
    return full_name

async def search_truck_details(truck_number):
    """
    Searches for truck details in the 'group_credentials' table based on the truck number.

    Args:
        truck_number (str): Truck number to search for.

    Returns:
        list: List of dictionaries with truck details (company name, driver name, group name, etc.).
    """
    sql = """
    SELECT truck_number, company_name, driver_name, group_name, group_id
    FROM group_credentials
    WHERE truck_number ILIKE $1
    """
    results = await db.execute(sql, f"%{truck_number}%", fetch=True)
    return [{"Truck Number": row["truck_number"], "Company Name": row["company_name"], "Driver Name": row["driver_name"], "Group Name": row["group_name"], "Group ID": row["group_id"]} for row in results]

async def append_load_assignment_data(load_data):
    """
    Inserts load assignment data into the 'gross_sheet' table in PostgreSQL.

    Args:
        load_data (list): A list containing the load assignment data.
    """
    sql = """
    INSERT INTO gross_sheet (
        load_number, company_name, dispatcher_name, driver_name, truck_number, broker_name,
        team_or_solo, pickup_location, pickup_datetime, delivery_location, delivery_datetime,
        deadhead_miles, loaded_miles, load_rate
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
    """
    await db.execute(sql, *load_data, execute=True)
