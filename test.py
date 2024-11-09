import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, bot
from aiogram.dispatcher import FSMContext


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

# user_data = {
#     "user_id": 123456789,                 # Telegram ID
#     "full_name": "Murodjon Abdullayev",   # Full Name
#     "date_of_birth": "26/03/1997",        # Date of Birth
#     "phone": "+99891 997 0326",           # Phone Number
#     "role": "Dispatcher"                  # Role
# }
#
# sheet = setup_google_sheets()
#
# add_user_to_sheet(sheet, user_data)

#
# # Function to send data to admin for approval
# @dp.callback_query_handler(text="✅ Send for Approval", state=FSMContext)
# async def send_to_admin_for_approval(call: types.CallbackQuery, state: FSMContext):
#     # Retrieve user data from FSM context
#     data = await state.get_data()
#     full_name = data.get("realName")
#     date_of_birth = data.get("dob")
#     phone = data.get("phoneNumber")
#
#     # Prepare the message for the admin
#     msg = (
#         f"New User Registration Request:\n\n"
#         f"Full Name: {full_name}\n"
#         f"Date of Birth: {date_of_birth}\n"
#         f"Phone Number: {phone}\n\n"
#         "Do you approve this registration?"
#     )
#
#     # Inline keyboard for admin's decision
#     admin_buttons = InlineKeyboardMarkup(row_width=2).add(
#         InlineKeyboardButton("✅ Approve", callback_data=f"approve_{call.from_user.id}"),
#         InlineKeyboardButton("❌ Deny", callback_data=f"deny_{call.from_user.id}")
#     )
#
#     # Replace with actual admin's Telegram ID
#     admin_id = 5159723225
#     # Send message to admin
#     await bot.send_message(admin_id, msg, reply_markup=admin_buttons)
#
#     # Notify user that their information has been sent to the admin
#     await call.message.edit_text(
#         "Your registration request has been sent to the admin for approval. Please wait for the response.")
#
#
# # Callback handler for admin approval or denial
# @dp.callback_query_handler(lambda call: call.data.startswith("approve_") or call.data.startswith("deny_"))
# async def process_admin_decision(call: types.CallbackQuery, state: FSMContext):
#     # Extract user ID and decision from callback data
#     action, user_id = call.data.split("_")
#     user_id = int(user_id)  # Convert to integer
#
#     # Retrieve user data from FSM context
#     user_data = await state.get_data()
#
#     if action == "approve":
#         # Add user ID and set role to "Dispatcher" as specified
#         user_data["user_id"] = user_id
#         user_data["role"] = "Dispatcher"
#
#         # Notify the user of approval
#         await bot.send_message(user_id, "✅ Your registration has been approved! Welcome to MoveMe Group.")
#
#         # Write user data to Google Sheet
#         sheet = setup_google_sheets()
#         add_user_to_sheet(sheet, user_data)
#
#         await call.answer("User approved and data written to Google Sheet.", show_alert=True)
#
#     elif action == "deny":
#         # Notify the user of denial
#         await bot.send_message(user_id,
#                                "❌ Your registration has been denied. Please contact support for more information.")
#         await call.answer("User denied.", show_alert=True)
#
#     # Finish the user's state now that the admin has made a decision
#     await state.finish()
#
#     # Delete the admin's decision message to keep the chat clean (optional)
#     await call.message.delete()
