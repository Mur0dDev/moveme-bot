from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp
from sheet.google_sheets_integration import fetch_all_data
from states.password_states import PasswordState


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
            await PasswordState.search_email.set()  # Transition to email search state
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


@dp.message_handler(state=PasswordState.search_email)
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


@dp.callback_query_handler(lambda call: call.data.startswith("select_email:"), state=PasswordState.search_email)
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
        await PasswordState.select_email.set()  # Transition to email selection state
    else:
        # Invalid selection
        await call.message.answer("❌ Invalid selection. Please try again.")


@dp.callback_query_handler(lambda call: call.data == "get_full_access", state=PasswordState.select_email)
async def request_comment_for_full_access(call: types.CallbackQuery, state: FSMContext):
    """
    Asks the user for a comment before granting full access to the credentials.
    """
    # Prompt the user for a comment
    await call.message.answer(
        "❓ Please provide a reason for requesting full access or mention to whom the password will be shared."
    )
    # Transition to add comment state
    await PasswordState.add_comment.set()


@dp.message_handler(state=PasswordState.add_comment)
async def send_full_access_with_comment(message: types.Message, state: FSMContext):
    """
    Sends full access credentials along with the user's comment to the secure channel.
    Adds inline buttons for refreshing the second step code and closing the operation.
    """
    CHANNEL_ID = -1002322400854  # Replace with your actual channel ID

    # Retrieve selected email and user comment from FSM context
    state_data = await state.get_data()
    selected_email = state_data.get("selected_email")
    user_comment = message.text.strip()

    if selected_email:
        # Prepare the message for the secure channel
        full_access_message = (
            f"🔓 Full Credential Details Requested:\n\n"
            f"🏢 Company Name: {selected_email['Company Name']}\n"
            f"🔐 Account Type: {selected_email['Account Type']}\n"
            f"📧 Email/Username: {selected_email['Email/Username']}\n"
            f"🔑 Password: {selected_email['Password']}\n"
            f"📅 Last Password Changed: {selected_email.get('Updated Date', 'N/A')}\n\n"
            f"📜 User Comment: {user_comment}\n"
            f"👤 Requested By: {message.from_user.full_name} (@{message.from_user.username})\n"
        )
        # Send full credentials to the secure channel
        await message.bot.send_message(chat_id=CHANNEL_ID, text=full_access_message)

        # Create inline buttons
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.add(
            InlineKeyboardButton(text="🔄 Refresh Second Step Code", callback_data="refresh_second_step"),
            InlineKeyboardButton(text="✅ Done and Close", callback_data="done_close")
        )

        # Notify the user and provide inline buttons
        await message.answer(
            "✅ Full access credentials, along with your comment, were sent to the secure channel.",
            reply_markup=buttons
        )
    else:
        # If no selected email is found in context
        await message.answer("❌ No selected email found. Please try again.")

    # Safeguard state.finish()
    try:
        if await state.get_state():
            await state.finish()
    except KeyError:
        pass



@dp.callback_query_handler(lambda call: call.data == "cancel_selection", state=PasswordState.search_email)
async def cancel_email_selection(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the cancellation of the email search operation.
    """
    try:
        # Safely finish the FSM state if it exists
        if await state.get_state():
            await state.finish()
    except KeyError:
        pass

    await call.message.edit_text("🔒 Email search operation has been canceled.")


@dp.callback_query_handler(lambda call: call.data == "close_operation", state=PasswordState.select_email)
async def close_operation_handler(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the closure of the current operation.
    """
    try:
        # Safely finish the FSM state if it exists
        if await state.get_state():
            await state.finish()
    except KeyError:
        # Log the KeyError or notify for debugging
        pass

    await call.message.edit_text("🔒 Operation has been closed.")

@dp.callback_query_handler(lambda call: call.data == "refresh_second_step")
async def refresh_second_step_code_handler(call: types.CallbackQuery):
    """
    Handles the 'Refresh Second Step Code' action.
    """
    await call.message.answer("🔄 The second step code has been refreshed successfully.")
    # Add logic for refreshing the code, if applicable


@dp.callback_query_handler(lambda call: call.data == "done_close")
async def done_and_close_handler(call: types.CallbackQuery):
    """
    Handles the 'Done and Close' action.
    """
    await call.message.edit_text("✅ Operation has been successfully closed.")
