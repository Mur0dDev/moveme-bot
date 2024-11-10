import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Check if user is in the Google Sheets credentials
def get_user_role_by_telegram_id(sheet, telegram_id):
    """
    Check if the user exists in the Google Sheet by Telegram ID and return their role.
    """
    records = sheet.get_all_records()
    for record in records:
        if record["Telegram ID"] == telegram_id:
            return record["Role"]
    return None

# Set up Google Sheets credentials
def setup_google_sheets():
    # Use the JSON file path of your service account credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name("autobot.json", [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(creds)
    # Open the Google Sheet by name or ID
    sheet = client.open("MoveMeGroup Bot Credentials").sheet1  # Adjust if using a specific sheet name
    return sheet


# Function to add approved user data to Google Sheets
def add_user_to_sheet(sheet, user_data):
    # Prepare row data in the order of your Google Sheet columns
    row = [
        user_data["user_id"],  # Telegram ID
        user_data["full_name"],  # Full Name
        user_data["date_of_birth"],  # DOB
        user_data["phone"],  # Phone Number
        user_data["role"]  # Role ("Dispatcher" in this case)
    ]
    # Append the row to the Google Sheet
    sheet.append_row(row)


def get_full_name_by_user_id(user_id):
    # Set up the Google Sheets client and open the specific sheet
    sheet = setup_google_sheets()

    # Find the row that matches the given user ID
    try:
        cell = sheet.find(str(user_id))  # Find the cell with the user ID (assuming IDs are unique)

        # Retrieve the full name from the second column in the same row
        full_name = sheet.cell(cell.row, 2).value
        return full_name
    except gspread.exceptions.CellNotFound:
        return None  # Return None if the user ID was not found
