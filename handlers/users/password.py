from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp
from sheet.google_sheets_integration import fetch_all_data
from states.password_states import PasswordState
from aiogram.utils.exceptions import MessageNotModified
import pyotp
import logging


def generate_totp_code(secret_key: str) -> str:
    """
    Generates a 6-digit TOTP code using the provided secret key.
    The code refreshes every 30 seconds.

    :param secret_key: Base32-encoded secret key
    :return: 6-digit TOTP code
    """
    # Create a TOTP object with the provided key
    totp = pyotp.TOTP(secret_key)
    # Generate the current OTP
    return totp.now()


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
            f"🔎 Search Result <b>{idx}</b>:\n"
            f"🏢 Company Name: {entry['Company Name']}\n"
            f"🔐 Account Type: {entry['Account Type']}\n"
            f"📧 Email/Username: {entry['Email/Username']}\n\n"
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
        await call.message.edit_text(
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
    await call.message.edit_text(
        "❓ Please provide a reason for requesting full access or mention to whom the password will be shared."
    )
    # Transition to add comment state
    await PasswordState.add_comment.set()


@dp.message_handler(state=PasswordState.add_comment)
async def send_full_access_with_comment(message: types.Message, state: FSMContext):
    """
    Sends full access credentials along with the user's comment to the secure channel.
    Generates a time-based OTP code from the key and includes it in the message.
    """
    CHANNEL_ID = -1002322400854  # Replace with your actual channel ID

    # Retrieve selected email and user comment from FSM context
    state_data = await state.get_data()
    selected_email = state_data.get("selected_email")
    user_comment = message.text.strip()

    if selected_email:
        # Save the user comment in FSM context
        await state.update_data(user_comment=user_comment)

        # Generate the OTP code from the key
        secret_key = selected_email['Key']
        try:
            otp_code = generate_totp_code(secret_key)
        except Exception as e:
            otp_code = "Error generating OTP"
            logging.error(f"Failed to generate OTP for key {secret_key}: {e}")

        # Prepare the message for the secure channel
        full_access_message = (
            f"🔓 Full Credential Details Requested:\n\n"
            f"🏢 Company Name: {selected_email['Company Name']}\n"
            f"🔐 Account Type: {selected_email['Account Type']}\n"
            f"📅 Last Password Changed: {selected_email.get('Updated Date', 'N/A')}\n\n"
            f"📧 Email/Username: <code>{selected_email['Email/Username']}</code>\n"
            f"🔑 Password: <code>{selected_email['Password']}</code>\n"
            f"⏳ OTP Code: <code>{otp_code}</code>\n\n"
            f"📜 User Comment: {user_comment}\n"
            f"👤 Requested By: {message.from_user.full_name} (@{message.from_user.username})\n"
        )

        # Send full credentials to the secure channel
        sent_message = await message.bot.send_message(chat_id=CHANNEL_ID, text=full_access_message)

        # Store the secure channel message ID in FSM context
        await state.update_data(secure_channel_message_id=sent_message.message_id)

        # Create inline buttons
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.add(
            InlineKeyboardButton(text="🔄 Refresh Second Step Code", callback_data="refresh_second_step"),
            InlineKeyboardButton(text="✅ Done and Close", callback_data="done_close")
        )

        await PasswordState.refresh_otp.set()

        # Notify the user and provide inline buttons
        await message.answer(
            "✅ Full access credentials, along with your comment, were sent to the secure channel.",
            reply_markup=buttons
        )
    else:
        # If no selected email is found in context
        await message.answer("❌ No selected email found. Please try again.")



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


@dp.callback_query_handler(lambda call: call.data == "refresh_second_step", state=PasswordState.refresh_otp)
async def refresh_second_step_code_handler(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the 'Refresh Second Step Code' action.
    Updates the OTP code for the selected email and edits the secure channel message.
    """
    # Channel ID where the secure message was sent
    CHANNEL_ID = -1002322400854  # Replace with your actual channel ID

    # Retrieve selected email and secure channel message ID from FSM context
    state_data = await state.get_data()
    selected_email = state_data.get("selected_email")
    message_id = state_data.get("secure_channel_message_id")  # Retrieve the secure channel message ID
    user_comment = state_data.get("user_comment", "No comment provided")  # Default comment if missing
    refresh_counter = state_data.get("refresh_counter", 1)  # Initialize counter if not already present

    if selected_email and message_id:
        secret_key = selected_email.get("Key")
        if not secret_key:
            await call.message.answer("❌ Missing OTP Key for the selected email.")
            return

        try:
            # Increment the refresh counter
            refresh_counter += 1
            await state.update_data(refresh_counter=refresh_counter)

            # Generate a new OTP code
            otp_code = generate_totp_code(secret_key)

            # Prepare updated secure channel message
            updated_message = (
                f"🔓 Full Credential Details Requested (Updated OTP Code):\n\n"
                f"🏢 Company Name: {selected_email['Company Name']}\n"
                f"🔐 Account Type: {selected_email['Account Type']}\n"
                f"📅 Last Password Changed: {selected_email.get('Updated Date', 'N/A')}\n\n"
                f"📧 Email/Username: <code>{selected_email['Email/Username']}</code>\n"
                f"🔑 Password: <code>{selected_email['Password']}</code>\n"
                f"⏳ Generated OTP Code: <code>{otp_code}</code>\n\n"
                f"📜 User Comment: {user_comment}\n"
                f"👤 Requested By: {call.from_user.full_name} (@{call.from_user.username})\n"
                f"🔄 OTP Refresh Count: {refresh_counter}\n"
            )

            # Edit the secure channel message with the new OTP code
            await call.bot.edit_message_text(
                chat_id=CHANNEL_ID,
                message_id=message_id,
                text=updated_message
            )

            # Notify the user that the OTP code was refreshed
            await call.message.answer("🔄 OTP Code refreshed and updated in the secure channel.")
        except pyotp.exceptions.InvalidKeyError:
            await call.message.answer("❌ Invalid OTP Key format. Please contact admin.")
        except Exception as e:
            logging.error(f"Failed to refresh OTP for key {secret_key}: {e}")
            await call.message.answer("❌ Unable to refresh the OTP code. Please try again.")
    else:
        # Missing critical data in FSM context
        if not selected_email:
            await call.message.answer("❌ No selected email found to refresh OTP code.")
        if not message_id:
            await call.message.answer("❌ No secure channel message ID found to update.")




@dp.callback_query_handler(lambda call: call.data == "done_close", state=PasswordState.refresh_otp)
async def done_and_close_handler(call: types.CallbackQuery, state: FSMContext):
    """
    Handles the 'Done and Close' action.
    Finishes the state and informs the user they can use the /start command again.
    """
    try:
        # Safely finish the FSM state
        if await state.get_state():
            await state.finish()
    except Exception as e:
        logging.error(f"Error finishing state: {e}")

    # Send the completion message
    await call.message.edit_text(
        "✅ Operation has been successfully closed.\n\n"
        "You can now use the /start or /pwd command again to initiate a new session."
    )

