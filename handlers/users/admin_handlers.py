import logging
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from states.super_admin_states import GroupVerificationStates, CacheManagementStates
from keyboards.inline.super_admin_inline_keyboards import (
    get_verification_request_keyboard,
    get_group_verification_keyboard,
    get_group_type_selection_keyboard
)
from utils.misc.load_assignment_validations import validate_truck_number
from utils.misc.validators import validate_full_name
from loader import dp, bot
from data.config import ADMINS  # Assuming admin IDs are stored here
from filters import IsSuperAdmin, IsPrivate

# Update cache imports (if used for future integrations)
from sheet.google_sheets_integration import (
    add_group_to_google_sheet,
    update_group_cache,
    handle_update_command,
    user_cache,
    group_cache,
    update_cache,
    get_user_full_name_by_telegram_id,
    check_group_verification
)


@dp.message_handler(IsPrivate(), IsSuperAdmin(), commands=['update'])
async def update_cache_command(message: types.Message, state: FSMContext):
    """
    Updates the cache for user and group data from Google Sheets.
    """
    await message.answer("Updating cache... Please wait.")
    await CacheManagementStates.updating_cache.set()

    try:
        result_message = await handle_update_command()
        await message.answer(f"Cache updated successfully!\n\n{result_message}")
    except Exception as e:
        logging.exception(f"Error updating cache: {e}")
        await message.answer("Failed to update the cache. Please check the logs.")

    # Finish the state
    await state.finish()


# Request Admin Approval
@dp.callback_query_handler(lambda c: c.data == "request_admin_approval")
async def handle_admin_approval_request(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    group_id = callback_query.message.chat.id
    group_title = callback_query.message.chat.title
    full_name = f"User {user_id}"  # Placeholder if no full name is fetched

    # Save group info in FSM state
    await state.update_data(group_id=group_id, group_title=group_title, full_name=full_name)

    # Notify admin
    verification_message = (
        f"Group Verification Request\n\n"
        f"Requester: {full_name}\n"
        f"User ID: {user_id}\n"
        f"Group ID: {group_id}\n"
        f"Group Title: {group_title}\n\n"
        "Please approve or deny the request and specify the group type."
    )

    for admin_id in ADMINS:
        await bot.send_message(
            admin_id,
            verification_message,
            reply_markup=get_verification_request_keyboard(group_id=group_id)
        )

    await callback_query.message.edit_text("Your request has been sent to the admin for approval.")
    await callback_query.answer()


# Approve Group Handler
@dp.callback_query_handler(Text(startswith="approve_group:"))
async def handle_approve_group(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        _, group_id_str = callback_query.data.split(":")
        group_id = int(group_id_str)

        # Save group_id in FSM state
        await state.update_data(group_id=group_id)

        # Notify admin
        await callback_query.answer("Group approved!", show_alert=True)
        await callback_query.message.edit_text(
            "The group has been successfully approved. Please select the group type:",
            reply_markup=get_group_type_selection_keyboard(group_id)
        )

        # Set the state for group type selection
        await GroupVerificationStates.group_type.set()
    except Exception as e:
        await callback_query.answer("Failed to approve the group. Please check the logs.", show_alert=True)
        logging.exception(f"Error in handle_approve_group: {e}")


# Group Type Selection
@dp.callback_query_handler(Text(startswith="set_group_type:"), state=GroupVerificationStates.group_type)
async def handle_set_group_type(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        _, group_type, group_id_str = callback_query.data.split(":")
        group_id = int(group_id_str)

        # Retrieve group_title from FSM state
        data = await state.get_data()
        group_title = data.get("group_title")

        if group_type == "management":
            await callback_query.answer("This function is under development.", show_alert=True)
            await callback_query.message.edit_text("The Management Group feature is under development.")
        elif group_type == "drivers":
            # Save group_type to FSM state
            await state.update_data(group_type="drivers")

            # Prompt for company name
            await callback_query.answer("Drivers' Group selected. Please choose a company name.")
            await callback_query.message.edit_text(
                "Now please choose a company name from below:",
                reply_markup=get_group_verification_keyboard()
            )

            await GroupVerificationStates.company_name.set()
    except Exception as e:
        await callback_query.answer("Failed to set the group type. Please check the logs.", show_alert=True)
        logging.exception(f"Error in handle_set_group_type: {e}")


# Verify GM Cargo
@dp.callback_query_handler(Text(equals="verify_gm_cargo"), state=GroupVerificationStates.company_name)
async def handle_verify_gm_cargo(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(company_name="GM Cargo LLC")
    await callback_query.answer("GM Cargo LLC selected.")
    await callback_query.message.edit_text("GM Cargo LLC selected. Enter Truck Number:")
    await GroupVerificationStates.truck_number.set()


# Verify Elmir
@dp.callback_query_handler(Text(equals="verify_elmir"), state=GroupVerificationStates.company_name)
async def handle_verify_elmir(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(company_name="Elmir INC")
    await callback_query.answer("Elmir INC selected.")
    await callback_query.message.edit_text("Elmir INC selected. Enter Truck Number:")
    await GroupVerificationStates.truck_number.set()


# Truck Number Input
@dp.message_handler(state=GroupVerificationStates.truck_number)
async def enter_truck_number(message: types.Message, state: FSMContext):
    truck_number = message.text
    if not validate_truck_number(truck_number):
        await message.answer("Invalid truck number format. Please enter a valid Truck Number (e.g., A1234 or 1234B).")
        return
    await state.update_data(truck_number=truck_number)
    await message.answer("Please enter Driver Name:")
    await GroupVerificationStates.driver_name.set()


# Driver Name Input and Write to Google Sheet
@dp.message_handler(state=GroupVerificationStates.driver_name)
async def enter_driver_name(message: types.Message, state: FSMContext):
    driver_name = message.text
    if not validate_full_name(driver_name):
        await message.answer("Invalid name format. Please enter a valid Driver Name.")
        return

    # Save driver name in FSM state
    await state.update_data(driver_name=driver_name)

    # Retrieve all stored data
    data = await state.get_data()
    group_id = data.get("group_id")
    company_name = data.get("company_name")
    group_name = data.get("group_title")
    group_type = data.get("group_type")
    truck_number = data.get("truck_number")

    # Debugging: Confirm all data
    print(group_id, company_name, group_name, group_type, truck_number, driver_name)

    # Write data to Google Sheets
    try:
        add_group_to_google_sheet({
            "group_id": group_id,
            "company_name": company_name,
            "group_name": group_name,
            "group_type": group_type,
            "truck_number": truck_number,
            "driver_name": driver_name
        })

        await message.answer("All data successfully saved to Google Sheets.")
        update_group_cache()

    except Exception as e:
        logging.exception(f"Error writing data to Google Sheets: {e}")
        await message.answer("An error occurred while saving the data.")

    # Clear FSM state safely
    try:
        await state.finish()
    except KeyError as e:
        logging.warning(f"Attempted to finish FSM state, but the state was already cleared: {e}")