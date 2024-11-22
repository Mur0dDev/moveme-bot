from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from loader import dp
from sheet.google_sheets_integration import fetch_all_data

@dp.message_handler(Command("pwd"), state="*")
async def handle_pwd_command(message: types.Message, state: FSMContext):
    """
    Handler for /pwd command. Checks if the user's Telegram ID is in the Allowed Users list.
    """
    # Fetch allowed users from the Google Sheet
    data = fetch_all_data()
    allowed_users = data.get("allowed_users", [])

    # Check if the user's Telegram ID exists in the allowed list
    user_id = message.from_user.id
    user_info = next((user for user in allowed_users if str(user["Telegram ID"]) == str(user_id)), None)

    if user_info:
        # User is allowed
        await message.reply("✅ You have the right to use this feature.")
    else:
        # User is not allowed
        await message.reply(
            "❌ You do not have permission to use this feature. Please contact admin: @iamurod"
        )
