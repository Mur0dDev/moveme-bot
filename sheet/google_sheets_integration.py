import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Cache dictionaries for user and group data
user_cache = {}
group_cache = {}

# Function to set up Google Sheets credentials for User Credentials sheet
def setup_google_sheets():
    """
    Sets up Google Sheets connection to the "User Credentials" sheet.
    """
    creds = ServiceAccountCredentials.from_json_keyfile_name("autobot.json", [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(creds)
    user_credentials = client.open("MoveMeGroup Bot Credentials").worksheet("User Credentials")
    return user_credentials

# Function to set up Google Sheets credentials for Group Credentials sheet
def setup_group_credentials_sheet():
    """
    Sets up Google Sheets connection to the "Group Credentials" sheet.
    """
    creds = ServiceAccountCredentials.from_json_keyfile_name("autobot.json", [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(creds)
    group_credentials = client.open("MoveMeGroup Bot Credentials").worksheet("Group Credentials")
    return group_credentials

# Function to update the user cache
def update_user_cache():
    """
    Fetches all user data from the 'User Credentials' sheet and updates the user cache.
    """
    sheet = setup_google_sheets()
    records = sheet.get_all_records()

    # Update the cache with user data, using Telegram ID as the key
    global user_cache
    user_cache = {str(record["Telegram ID"]): record["Full Name"] for record in records}

# Function to update the group cache
def update_group_cache():
    """
    Fetches all group data from the 'Group Credentials' sheet and updates the group cache.
    """
    sheet = setup_group_credentials_sheet()
    records = sheet.get_all_records()

    # Update the cache with group data, using Group ID as the key
    global group_cache
    group_cache = {
        str(record["Group ID"]): {
            "Company Name": record["Company Name"],
            "Group Name": record["Group Name"],
            "Truck Number": record["Truck Number"],
            "Driver Name": record["Driver Name"]
        } for record in records
    }

# Function to clear cache and update both user and group caches
def update_cache():
    """
    Clears the existing cache and updates both user and group caches.
    """
    global user_cache, group_cache
    user_cache = {}
    group_cache = {}
    update_user_cache()
    update_group_cache()

# Function to get user full name from cache by Telegram ID
def get_user_full_name_by_telegram_id(telegram_id: int) -> str:
    """
    Checks if the user is registered by looking up their Telegram ID in the cache.
    Returns the full name if registered, otherwise returns None.
    """
    return user_cache.get(str(telegram_id))  # Using cache instead of Google Sheets

# Function to check if a group is verified from cache by Group ID
def check_group_verification(group_id: int) -> bool:
    """
    Checks if the group is verified by looking up the Group ID in the cache.
    Returns True if the group is verified, otherwise returns False.
    """
    return str(group_id) in group_cache  # Using cache instead of Google Sheets

# Additional function to handle /update command if called from bot
async def handle_update_command():
    """
    Function to handle cache update when the /update command is issued by an admin.
    """
    update_cache()
    return "Cache updated successfully with the latest data from Google Sheets."

# Functions not involved in the caching process:

def get_user_role_by_telegram_id(telegram_id: int) -> str:
    """
    Checks if the user exists in the cache by Telegram ID and returns their role.
    If not found, returns None.
    """
    user_data = user_cache.get(str(telegram_id))
    if user_data:
        return user_data.get("Role")
    return None

def add_user_to_sheet(sheet, user_data):
    """
    Function to add approved user data to Google Sheets.
    """
    row = [
        user_data["user_id"],  # Telegram ID
        user_data["full_name"],  # Full Name
        user_data["date_of_birth"],  # DOB
        user_data["phone"],  # Phone Number
        user_data["role"]  # Role ("Dispatcher" in this case)
    ]
    sheet.append_row(row)

def get_full_name_by_user_id(user_id: int) -> str:
    """
    Retrieves the full name of a user from the cache by their Telegram ID.
    If not found, returns None.
    """
    user_data = user_cache.get(str(user_id))
    if user_data:
        return user_data.get("Full Name")
    return None
