import logging
from aiogram import types
from aiogram.dispatcher.filters import Text

from keyboards.inline.super_admin_inline_keyboards import get_verification_request_keyboard, get_group_verification_keyboard
from loader import dp, bot
from sheet.google_sheets_integration import add_group_to_google_sheet, update_group_cache
from sheet.google_sheets_integration import handle_update_command, user_cache, group_cache, update_cache, \
    get_user_full_name_by_telegram_id, check_group_verification
from filters import IsSuperAdmin, IsPrivate
from data.config import ADMINS  # Assuming admin IDs are stored here


# Handler for group approval requests
@dp.callback_query_handler(lambda c: c.data.startswith("approve_group"))
async def handle_group_approval_request(callback_query: types.CallbackQuery):
    """
    Handles group approval requests by writing data to Google Sheets and updating the cache memory.
    """
    admin_id = callback_query.from_user.id
    if admin_id not in dp.bot['ADMINS']:
        await callback_query.answer("You do not have permission to perform this action.", show_alert=True)
        return

    # Extract data from callback query or temporary storage (e.g., cache)
    group_data = dp.bot.get("pending_group_data")  # Example: Temporary data for approval
    if not group_data:
        await callback_query.answer("No group data found for approval.", show_alert=True)
        return

    # Write group data to Google Sheets
    try:
        add_group_to_google_sheet(group_data)  # Write to the Google Sheet
        update_group_cache()  # Update the cache memory
        await callback_query.answer("Group approved and data successfully updated.", show_alert=True)
        await callback_query.message.edit_text("Group approved and added to the system.")
    except Exception as e:
        await callback_query.answer("Failed to update group data. Please check the system logs.", show_alert=True)
        logging.exception(f"Error updating group data: {e}")

@dp.message_handler(IsPrivate(), IsSuperAdmin(), commands=['update'])
async def update_cache_command(message: types.Message):
    """
    Handler for the /update command. This command updates the cache for user and group data from Google Sheets.
    Only the super admin can execute this command.
    """
    # Await the update command and get the result message
    result_message = await handle_update_command()

    # Prepare a detailed report of the updated data
    user_data_summary = "\n".join([f"Telegram ID: {telegram_id}, Full Name: {data}" for telegram_id, data in user_cache.items()])
    group_data_summary = "\n".join([f"Group ID: {group_id}, Data: {data}" for group_id, data in group_cache.items()])

    # Compile the response message with cache summary
    response = f"{result_message}\n\nUpdated User Data:\n{user_data_summary}\n\nUpdated Group Data:\n{group_data_summary}"

    # Send the detailed update message to the admin
    await message.reply(result_message)

@dp.callback_query_handler(lambda c: c.data == "request_admin_approval")
async def handle_admin_approval_request(callback_query: types.CallbackQuery):
    """
    Handles the 'Admin Approval' button press to send a verification request to admin.
    """
    user_id = callback_query.from_user.id
    group_id = callback_query.message.chat.id
    group_title = callback_query.message.chat.title
    full_name = get_user_full_name_by_telegram_id(user_id) or "Unknown User"

    # Message to send to the admin
    verification_message = (
        f"Group Verification Request\n\n"
        f"Requester: {full_name}\n"
        f"User ID: {user_id}\n"
        f"Group ID: {group_id}\n"
        f"Group Title: {group_title}\n\n"
        "Please approve or deny the request and specify the group type."
    )

    # Send the verification message to each admin
    for admin_id in ADMINS:
        await bot.send_message(admin_id, verification_message, reply_markup=get_verification_request_keyboard())

    # Notify the user that their request has been sent to the admin
    await callback_query.message.edit_text("Your request has been sent to the admin for approval.", reply_markup=None)
    await callback_query.answer()  # Acknowledge the callback

@dp.callback_query_handler(lambda c: c.data == "close_request")
async def handle_close_request(callback_query: types.CallbackQuery):
    """
    Handles the 'Close' button press to delete the request message.
    """
    # Delete the message
    await callback_query.message.delete()
    await callback_query.answer()  # Acknowledge the callback

@dp.callback_query_handler(lambda c: c.data == "approve_request")
async def handle_approve_group(callback_query: types.CallbackQuery):
    await callback_query.answer(f"Group approved!")
    await callback_query.message.edit_text(f"Group has been successfully approved.", reply_markup=get_group_verification_keyboard)


@dp.callback_query_handler(lambda c: c.data == "deny_request")
async def handle_deny_group(callback_query: types.CallbackQuery):
    """
    Handles the 'Deny Group' button and notifies the group.
    """
    try:
        # Extract group ID from callback data
        callback_data = callback_query.data
        _, group_id_str = callback_data.split(":")  # Split callback data by ':'

        # Ensure group ID is a valid integer
        if not group_id_str.isdigit():
            raise ValueError("Invalid group ID format.")

        group_id = int(group_id_str)  # Convert to integer
        admin_username = callback_query.from_user.username

        # Notify the admin in the callback
        await callback_query.answer("Group denied!")

        # Notify the group about the denial
        denial_message = (
            f"This group is not approved for bot usage by the bot admin @{admin_username}. "
            "Please contact them for more information."
        )
        await callback_query.bot.send_message(chat_id=group_id, text=denial_message)

        # Edit the original message for the admin
        await callback_query.message.edit_text("Group has been denied.")

    except ValueError as e:
        # Log and notify about invalid callback data
        await callback_query.answer("Invalid callback data!", show_alert=True)
        print(f"Error processing deny_group callback: {e}")


@dp.callback_query_handler(Text(equals="verify_gm_cargo"))
async def handle_verify_gm_cargo(callback_query: types.CallbackQuery):
    """
    Handles the "GM Cargo LLC" button.
    """
    await callback_query.answer("You selected GM Cargo LLC.")
    await callback_query.message.edit_text("GM Cargo LLC selected for verification.\n")

@dp.callback_query_handler(Text(equals="verify_elmir"))
async def handle_verify_elmir(callback_query: types.CallbackQuery):
    """
    Handles the "Elmir INC" button.
    """
    await callback_query.answer("You selected Elmir INC.")
    await callback_query.message.edit_text("Elmir INC selected for verification.")

@dp.callback_query_handler(Text(equals="close_verification"))
async def handle_close_verification(callback_query: types.CallbackQuery):
    """
    Handles the "Close" button.
    """
    await callback_query.answer("Verification process closed.")
    await callback_query.message.delete()