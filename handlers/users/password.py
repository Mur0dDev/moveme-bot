from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from google_sheets_integration import get_data_from_sheet, write_to_sheet
from loader import dp


@dp.message_handler(Command("get_credentials"))
async def get_credentials(message: types.Message):
    # Validate if the user is allowed
    user_id = message.from_user.id
    allowed_users = get_data_from_sheet(sheet_name="Allowed Users")
    user_info = next((user for user in allowed_users if str(user["Telegram ID"]) == str(user_id)), None)

    if not user_info or user_info["Status"] != "Active":
        await message.reply("You are not authorized to access password credentials. Contact admin for assistance.")
        return

    # Ask the user for the company name or account type
    await message.reply("Please provide the Company Name or Account Type for the credentials you want to access.")


@dp.message_handler(state=None)
async def fetch_credentials(message: types.Message):
    query = message.text.strip()
    pwd_data = get_data_from_sheet(sheet_name="PWD Credentials")

    # Filter data based on user input
    results = [row for row in pwd_data if query.lower() in row["Company Name"].lower() or query.lower() in row["Account Type"].lower()]

    if not results:
        await message.reply("No credentials found for the provided input. Please check and try again.")
        return

    # Format and send response
    response = "\n".join(
        [
            f"Company: {row['Company Name']}\n"
            f"Account Type: {row['Account Type']}\n"
            f"Email/Username: {row['Email/Username']}\n"
            f"Password: {'********'} (hidden)\n"
            f"Key: {row['Key']}\n"
            f"Notes: {row['Notes']}\n"
            f"URL: {row['URL/Link']}\n"
            for row in results
        ]
    )
    await message.reply(f"Here are the credentials found:\n\n{response}")

    # Log the access
    write_to_sheet(
        sheet_name="Access Logs",
        data=[
            {
                "Date and Time": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                "User Telegram ID": message.from_user.id,
                "User Full Name": message.from_user.full_name,
                "Accessed Account Type": query,
                "Result": "Granted",
                "Remarks": "Successful access",
            }
        ],
    )


@dp.callback_query_handler(lambda call: call.data.startswith("reveal_password"))
async def reveal_password(call: types.CallbackQuery):
    # Extract company or account type from callback data
    _, company_name = call.data.split(":")
    pwd_data = get_data_from_sheet(sheet_name="PWD Credentials")
    credentials = next((row for row in pwd_data if row["Company Name"] == company_name), None)

    if credentials:
        await call.message.edit_text(
            f"Company: {credentials['Company Name']}\n"
            f"Account Type: {credentials['Account Type']}\n"
            f"Email/Username: {credentials['Email/Username']}\n"
            f"Password: {credentials['Password']}\n"
            f"Key: {credentials['Key']}\n"
            f"Notes: {credentials['Notes']}\n"
            f"URL: {credentials['URL/Link']}\n"
        )
    else:
        await call.message.reply("Could not retrieve the password. Please try again.")


def log_access(user_id, full_name, account_type, result, remarks):
    write_to_sheet(
        sheet_name="Access Logs",
        data=[
            {
                "Date and Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "User Telegram ID": user_id,
                "User Full Name": full_name,
                "Accessed Account Type": account_type,
                "Result": result,
                "Remarks": remarks,
            }
        ],
    )
