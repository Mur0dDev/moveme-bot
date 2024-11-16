import logging
from aiogram import types
from aiogram.dispatcher.filters import Text

from aiogram.dispatcher import FSMContext
from states.assign_load_states import AssignLoad
from keyboards.inline.super_admin_inline_keyboards import get_verification_request_keyboard, get_group_verification_keyboard, get_group_type_selection_keyboard
from utils.misc.load_assignment_validations import validate_truck_number
from utils.misc.validators import validate_full_name
from loader import dp, bot
from sheet.google_sheets_integration import add_group_to_google_sheet, update_group_cache
from sheet.google_sheets_integration import handle_update_command, user_cache, group_cache, update_cache, \
    get_user_full_name_by_telegram_id, check_group_verification
from filters import IsSuperAdmin, IsPrivate
from data.config import ADMINS  # Assuming admin IDs are stored here


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
        await bot.send_message(
            admin_id,
            verification_message,
            reply_markup=get_verification_request_keyboard(group_id=group_id)  # Pass the group ID here
        )

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

@dp.callback_query_handler(Text(startswith="approve_group:"))
async def handle_approve_group(callback_query: types.CallbackQuery):
    """
    Handles the 'Approve Group' button, processes group approval, and asks for group type.
    """
    try:
        # Extract the group_id from callback data
        _, group_id_str = callback_query.data.split(":")
        group_id = int(group_id_str)

        # Notify the admin about the approval
        await callback_query.answer("Group approved!", show_alert=True)
        await callback_query.message.edit_text(
            "The group has been successfully approved. Please select the group type:",
            reply_markup=get_group_type_selection_keyboard(group_id)
        )

    except Exception as e:
        await callback_query.answer("Failed to approve the group. Please check the logs.", show_alert=True)
        logging.exception(f"Error in handle_approve_group: {e}")


@dp.callback_query_handler(Text(startswith="deny_group:"))
async def handle_deny_group(callback_query: types.CallbackQuery):
    """
    Handles the 'Deny Group' button, processes group denial.
    """
    try:
        # Extract the group_id from callback data
        _, group_id_str = callback_query.data.split(":")
        group_id = int(group_id_str)

        # Notify the admin
        await callback_query.answer("Group denied!", show_alert=True)
        await callback_query.message.edit_text("The group has been denied.")

        # Notify the group about the denial
        denial_message = (
            f"This group is not approved for bot usage by the bot admin @{callback_query.from_user.username}. "
            "Please contact them for more information."
        )
        await bot.send_message(chat_id=group_id, text=denial_message)

    except Exception as e:
        await callback_query.answer("Failed to deny the group. Please check the logs.", show_alert=True)
        logging.exception(f"Error in handle_deny_group: {e}")

@dp.callback_query_handler(Text(startswith="set_group_type:"))
async def handle_set_group_type(callback_query: types.CallbackQuery):
    """
    Handles the selection of the group type by the super admin.
    """
    try:
        # Parse the callback data
        _, group_type, group_id_str = callback_query.data.split(":")
        group_id = int(group_id_str)

        if group_type == "management":
            # Notify about the under-development status for Management Group
            await callback_query.answer("This function is under development. Please wait a little.", show_alert=True)
            await callback_query.message.edit_text("The Management Group feature is currently under development.")
        elif group_type == "drivers":
            # Prompt for company name selection for Drivers' Group
            await callback_query.answer("Drivers' Group selected. Please choose a company name.")
            await callback_query.message.edit_text(
                "Now please choose a company name from below:",
                reply_markup=get_group_verification_keyboard()  # Assuming this provides company options
            )
        else:
            # Handle unexpected group types
            await callback_query.answer("Invalid group type selected. Please try again.", show_alert=True)

    except Exception as e:
        await callback_query.answer("Failed to set the group type. Please check the logs.", show_alert=True)
        logging.exception(f"Error in handle_set_group_type: {e}")

@dp.callback_query_handler(Text(equals="verify_gm_cargo"))
async def handle_verify_gm_cargo(callback_query: types.CallbackQuery):
    """
    Handles the "GM Cargo LLC" button.
    """
    await callback_query.answer("You selected GM Cargo LLC.")
    await callback_query.message.edit_text("GM Cargo LLC selected for verification.\n\nEnter Truck number:")
    await AssignLoad.truck_number.set()

@dp.callback_query_handler(Text(equals="verify_elmir"))
async def handle_verify_elmir(callback_query: types.CallbackQuery):
    """
    Handles the "Elmir INC" button.
    """
    await callback_query.answer("You selected Elmir INC.")
    await callback_query.message.edit_text("Elmir INC selected for verification.\n\nEnter Truck number:")
    await AssignLoad.truck_number.set()

@dp.callback_query_handler(Text(equals="close_verification"))
async def handle_close_verification(callback_query: types.CallbackQuery):
    """
    Handles the "Close" button.
    """
    await callback_query.answer("Verification process closed.")
    await callback_query.message.delete()

# Handler for Truck Number input with validation
@dp.message_handler(state=AssignLoad.truck_number)
async def enter_truck_number(message: types.Message, state: FSMContext):
    truck_number = message.text
    if not validate_truck_number(truck_number):
        await message.answer("Invalid truck number format. Please enter a valid Truck Number (e.g., A1234 or 1234B).")
        return
    await state.update_data(truck_number=truck_number)
    await message.answer("Please enter driver full name:")
    await AssignLoad.driver_name.set()

@dp.message_handler(state=AssignLoad.driver_name)
async def enter_driver_name(message: types.Message, state: FSMContext):
    driver_name = message.text

    # Validate the driver name
    if not validate_full_name(driver_name):
        await message.answer("Invalid name format. Please enter a valid Driver Name.")
        return  # Stop here if the name is invalid, allowing user to retry

    # If valid, store the name and proceed to the next step
    await state.update_data(driver_name=driver_name)

    await message.answer("So far all good")