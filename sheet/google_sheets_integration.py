import gspread
from oauth2client.service_account import ServiceAccountCredentials
# from datetime import datetime
# # from aiogram import types
# # from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# # from loader import dp, bot
# # from aiogram.dispatcher import FSMContext


# Set up Google Sheets credentials
def setup_google_sheets():
    # Use the JSON file path of your service account credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name("../autobot.json", [
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
