import os
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from difflib import get_close_matches


json_file_path = "C:\\Users\\user\\PycharmProjects\\moveme-bot\\autobot.json"
home_json_file_path = "E:\\GitHub Projects\\moveme-bot\\autobot.json"

# Cache dictionaries for user and group data
user_cache = {}
group_cache = {}

# Function to set up Google Sheets credentials for User Credentials sheet
def setup_google_sheets():
    """
    Sets up Google Sheets connection to the "User Credentials" sheet.
    """
    print("Setting up Google Sheets connection for User Credentials...")
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_file_path, [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(creds)
    user_credentials = client.open("MoveMeGroup Bot Credentials").worksheet("User Credentials")
    print("User Credentials sheet connected.")
    return user_credentials

# Function to set up Google Sheets credentials for Group Credentials sheet
def setup_group_credentials_sheet():
    """
    Sets up Google Sheets connection to the "Group Credentials" sheet.
    """
    print("Setting up Google Sheets connection for Group Credentials...")
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_file_path, [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(creds)
    group_credentials = client.open("MoveMeGroup Bot Credentials").worksheet("Group Credentials")
    print("Group Credentials sheet connected.")
    return group_credentials

# Function to update the user cache
def update_user_cache():
    """
    Fetches all user data from the 'User Credentials' sheet and updates the user cache.
    """
    print("Updating user cache...")
    sheet = setup_google_sheets()
    records = sheet.get_all_records()
    print(f"Fetched {len(records)} records from User Credentials sheet.")

    # Update the cache with user data, using Telegram ID as the key
    global user_cache
    user_cache = {str(record["Telegram ID"]): record for record in records}
    print("User cache updated.")

# Function to update the group cache
def update_group_cache():
    """
    Fetches all group data from the 'Group Credentials' sheet and updates the group cache.
    """
    print("Updating group cache...")
    sheet = setup_group_credentials_sheet()
    records = sheet.get_all_records()
    print(f"Fetched {len(records)} records from Group Credentials sheet.")

    # Update the cache with group data, using Group ID as the key
    global group_cache
    group_cache = {}

    for record in records:
        # Ensure all required fields exist in the record
        try:
            group_id = str(record["Group ID"])
            group_cache[group_id] = {
                "Company Name": record.get("Company Name"),
                "Group Name": record.get("Group Name"),
                "Group Type": record.get("Group Type"),
                "Truck Number": record.get("Truck Number"),
                "Driver Name": record.get("Driver Name"),
                "Group ID": record.get("Group ID"),  # Explicitly include Group ID
            }
        except KeyError as e:
            print(f"Error processing record {record}: Missing key {e}")
            continue

    print("Group cache updated:", group_cache)


# Function to clear cache and update both user and group caches
def update_cache():
    """
    Clears the existing cache and updates both user and group caches.
    """
    print("Clearing and updating cache...")
    global user_cache, group_cache
    user_cache = {}
    group_cache = {}
    update_user_cache()
    update_group_cache()
    print("Cache updated successfully.")

# Function to get user full name from cache by Telegram ID
def get_user_full_name_by_telegram_id(telegram_id: int) -> str:
    """
    Checks if the user is registered by looking up their Telegram ID in the cache.
    Returns the full name if registered, otherwise returns None.
    """
    print(f"Looking up full name for Telegram ID: {telegram_id}")
    full_name = user_cache.get(str(telegram_id), {}).get("Full Name")
    print(f"Full name found: {full_name}")
    return full_name

# Function to check if a group is verified from cache by Group ID
def check_group_verification(group_id: int) -> bool:
    """
    Checks if the group is verified by looking up the Group ID in the cache.
    Returns True if the group is verified, otherwise returns False.
    """
    print(f"Checking if group ID {group_id} is verified...")
    is_verified = str(group_id) in group_cache
    print(f"Group verification status: {is_verified}")
    return is_verified

# Additional function to handle /update command if called from bot
async def handle_update_command():
    """
    Function to handle cache update when the /update command is issued by an admin.
    """
    print("Handling /update command: updating cache...")
    update_cache()
    print("Cache update completed.")
    return "Cache updated successfully with the latest data from Google Sheets."

# Functions not involved in the caching process:

def get_user_role_by_telegram_id(telegram_id: int) -> str:
    """
    Checks if the user exists in the cache by Telegram ID and returns their role.
    If not found, returns None.
    """
    print(f"Fetching user role for Telegram ID: {telegram_id}")
    user_data = user_cache.get(str(telegram_id))
    role = user_data.get("Role") if user_data else None
    print(f"Role found: {role}")
    return role

def add_user_to_sheet(sheet, user_data):
    """
    Function to add approved user data to Google Sheets.
    """
    print(f"Adding user {user_data['user_id']} to Google Sheets...")
    row = [
        user_data["user_id"],  # Telegram ID
        user_data["full_name"],  # Full Name
        user_data["date_of_birth"],  # DOB
        user_data["phone"],  # Phone Number
        user_data["role"]  # Role ("Dispatcher" in this case)
    ]
    sheet.append_row(row)
    print("User added to Google Sheets.")

def add_group_to_google_sheet(group_data):
    """
    Writes group data to the 'Group Credentials' sheet in Google Sheets.
    """
    try:
        sheet = setup_group_credentials_sheet()
        sheet.append_row([
            group_data["group_id"],
            group_data["company_name"],
            group_data["group_name"],
            group_data["group_type"],
            group_data["truck_number"],
            group_data["driver_name"],
        ])
        print("Group data successfully written to Google Sheets.")
    except Exception as e:
        logging.exception(f"Error writing to Google Sheets: {e}")
        raise


def get_full_name_by_user_id(user_id: int) -> str:
    """
    Retrieves the full name of a user from the cache by their Telegram ID.
    If not found, returns None.
    """
    print(f"Retrieving full name for user ID: {user_id}")
    full_name = user_cache.get(str(user_id), {}).get("Full Name")
    print(f"Full name found: {full_name}")
    return full_name


# Test Cases

def search_truck_details(truck_number: str) -> list:
    """
    Searches for truck details in the group_cache based on the given truck number.
    Retrieves similar matches with company name, driver name, and group name.

    Args:
        truck_number (str): The truck number to search for.

    Returns:
        list: A list of dictionaries with truck details (company name, driver name, group name, truck number).
    """
    print(f"Searching for truck details matching: {truck_number}")

    # Gather all truck numbers from the group_cache
    truck_entries = [
        {
            "Truck Number": value["Truck Number"],
            "Company Name": value["Company Name"],
            "Driver Name": value["Driver Name"],
            "Group Name": value["Group Name"],
            "Group ID": value["Group ID"],
        }
        for value in group_cache.values()
    ]

    # Get all truck numbers as strings for matching
    truck_numbers = [str(entry["Truck Number"]) for entry in truck_entries]

    # Find close matches for the truck number
    similar_trucks = get_close_matches(truck_number, truck_numbers, n=5, cutoff=0.5)

    # Filter truck details for the matched truck numbers
    results = [
        entry for entry in truck_entries if str(entry["Truck Number"]) in similar_trucks
    ]

    if results:
        print(f"Found matching trucks: {results}")
    else:
        print("No matching trucks found.")

    return results

# if __name__ == "__main__":
#     # Step 1: Update the cache with the latest data
#     update_cache()
#
#     test_search_company_name()
#     test_search_driver_name()
#     test_search_truck_number()
#
#     Step 2: Print the caches to verify data
#     print("User Cache:", user_cache)
#     print("Group Cache:", group_cache)
#
#     print(search_truck_details("415"))
#
#     # Optional Step 3: Test retrieval functions with sample IDs
#     test_telegram_id = 6697656102  # Replace with actual Telegram ID
#     test_group_id = 987654321  # Replace with actual Group ID
#
#     user_full_name = get_user_full_name_by_telegram_id(test_telegram_id)
#     print(f"User Full Name for Telegram ID {test_telegram_id}: {user_full_name}")
#
#     is_group_verified = check_group_verification(test_group_id)`
#     print(f"Is Group {test_group_id} Verified? {is_group_verified}")
