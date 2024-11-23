from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from loader import dp
from sheet.google_sheets_integration import fetch_all_data
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@dp.message_handler(Command("pwd"), state="*")
async def handle_pwd_command(message: types.Message, state: FSMContext):
    """
    Handler for /pwd command. Checks if the user's Telegram ID, name, and status are valid in the Allowed Users list.
    """
    # Fetch allowed users from the Google Sheet
    data = fetch_all_data()
    allowed_users = data.get("allowed_users", [])

    # Extract the user's Telegram ID
    user_id = message.from_user.id
    # Find the user in the Allowed Users list
    user_info = next((user for user in allowed_users if str(user["Telegram ID"]) == str(user_id)), None)

    if user_info:
        # User exists in the Allowed Users list
        user_name = user_info.get("Full Name", "Unknown User")
        user_status = user_info.get("Status", "Inactive")

        if user_status.lower() == "active":
            # User is active and allowed
            await message.reply(f"✅ Hello, {user_name}! You have the right to use this feature.\n"
                                f"Please enter an email to search:")
        else:
            # User exists but is inactive
            await message.reply(
                f"❌ Hello, {user_name}. Your status has been inactivated by the admin, @iamurod. Please contact them."
            )
    else:
        # User does not exist in the Allowed Users list
        await message.reply(
            "❌ You do not have access to this feature. Please contact admin: @iamurod."
        )


@dp.message_handler(state="*")
async def search_email_handler(message: types.Message, state: FSMContext):
    """
    Searches for email in the Email/Username column of the PWD Credentials sheet and returns similar options.
    """
    email_query = message.text.strip()

    # Fetch PWD Credentials data from Google Sheets
    data = fetch_all_data()
    pwd_credentials = data.get("pwd_credentials", [])

    # Search for emails matching the user's query
    matched_emails = [
        entry for entry in pwd_credentials
        if email_query.lower() in entry["Email/Username"].lower()
    ]

    if not matched_emails:
        # No matches found
        await message.answer(
            f"❌ No Matches Found:\n\nWe couldn’t find any credentials matching '{email_query}'. Please double-check and try again."
        )
        return

    # Save matched emails in FSM context
    await state.update_data(matched_emails=matched_emails)

    # Create a numbered list of results
    results_message = "🔎 Search Results:\nHere are the credentials matching your query:\n\n"
    for idx, entry in enumerate(matched_emails, start=1):
        results_message += (
            f"🔎 Search Result {idx}:\n"
            f"🏢 Company Name: {entry['Company Name']}\n"
            f"🔐 Account Type: {entry['Account Type']}\n"
            f"📧 Email/Username: {entry['Email/Username']}\n"
        )

    # Generate inline buttons for selecting a result
    email_buttons = InlineKeyboardMarkup(row_width=5)
    for idx in range(1, len(matched_emails) + 1):
        email_buttons.insert(InlineKeyboardButton(
            text=str(idx),
            callback_data=f"select_email:{idx}"
        ))

    # Add cancel button
    email_buttons.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_selection"))

    # Send the results and inline buttons
    await message.answer(results_message, reply_markup=email_buttons)


@dp.callback_query_handler(lambda call: call.data.startswith("select_email:"))
async def handle_email_selection(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the selection of an email search result based on the provided callback data.
    Adds inline buttons for 'Get Full Access' and 'Close'.
    """
    # Extract the index from the callback data
    index = int(call.data.split(":")[1]) - 1  # Convert to zero-based index

    # Retrieve matched emails from FSM context
    state_data = await state.get_data()
    matched_emails = state_data.get("matched_emails", [])

    if index < len(matched_emails):
        # Get the selected entry
        selected_email = matched_emails[index]

        # Save selected entry in FSM context for further actions
        await state.update_data(selected_email=selected_email)

        # Format and send the selected information with inline buttons
        await call.message.answer(
            f"🔎 Selected Credential Details:\n\n"
            f"🏢 Company Name: {selected_email['Company Name']}\n"
            f"🔐 Account Type: {selected_email['Account Type']}\n"
            f"📧 Email/Username: {selected_email['Email/Username']}\n"
            f"📅 Last Password Changed: {selected_email.get('Updated Date', 'N/A')}\n",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔓 Get Full Access", callback_data="get_full_access")],
                    [InlineKeyboardButton(text="❌ Close", callback_data="close_operation")],
                ]
            ),
        )
    else:
        # Invalid selection
        await call.message.answer("❌ Invalid selection. Please try again.")


@dp.callback_query_handler(lambda call: call.data == "cancel_selection")
async def cancel_email_selection(call: types.CallbackQuery):
    """
    Handles the cancellation of the email search operation.
    """
    await call.message.edit_text("🔒 Email search operation has been canceled.")

@dp.callback_query_handler(lambda call: call.data == "close_operation")
async def close_operation_handler(call: types.CallbackQuery):
    """
    Handles the closure of the current operation.
    """
    await call.message.edit_text("🔒 Operation has been closed.")

@dp.callback_query_handler(lambda call: call.data == "get_full_access")
async def get_full_access_handler(call: types.CallbackQuery, state: FSMContext):
    """
    Sends full credential details, including sensitive information like the password, to a specific channel.
    Notifies the user that the details were sent.
    """
    # Replace with the ID of your target channel
    CHANNEL_ID = -1002322400854  # Replace with your actual channel ID

    # Retrieve selected email from FSM context
    state_data = await state.get_data()
    selected_email = state_data.get("selected_email")

    if selected_email:
        # Send full details to the specified channel
        full_access_message = (
            f"🔓 Full Credential Details:\n\n"
            f"🏢 Company Name: {selected_email['Company Name']}\n"
            f"🔐 Account Type: {selected_email['Account Type']}\n"
            f"📧 Email/Username: {selected_email['Email/Username']}\n"
            f"🔑 Password: {selected_email['Password']}\n"
            f"📅 Last Password Changed: {selected_email.get('Updated Date', 'N/A')}\n"
        )
        await call.bot.send_message(chat_id=CHANNEL_ID, text=full_access_message)

        # Notify the user
        await call.message.answer("✅ Full access credentials were sent to the secure channel.")
    else:
        # If no selected email is found in context
        await call.message.answer("❌ No selected email found. Please try again.")



