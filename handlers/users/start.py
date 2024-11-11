# Imports
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from filters import IsPrivate
from keyboards.inline.new_user_inline_keyboard import new_user_letsgo, pickup_department
from keyboards.inline.admin_approval_new_user_reg import admin_approval_new_user
from sheet.google_sheets_integration import setup_google_sheets, add_user_to_sheet, get_user_role_by_telegram_id
from data.texts import (
    get_random_message,
    name_error_messages,
    dob_error_messages,
    phone_error_messages,
    name_prompt_messages,
    dob_prompt_messages,
    phone_prompt_messages,
    welcome_messages,
    under_development_messages,
    approval_request_messages,
    approval_success_messages,
    denial_messages,
    department_prompt_messages,
    approval_sheet_messages,
    denial_confirmation_messages
)

from utils.misc.validators import validate_full_name, validate_dob, validate_uzbekistan_phone
from utils.misc.temp_data import temp_user_data

from loader import dp, bot
from states.dispatcher_reg_data import PersonalData, DispatchState, SafetyState, DriverState, AccountingState, DeniedState, UnverifiedState

# ------------------------------
# Start Command Handler
# ------------------------------

@dp.message_handler(IsPrivate(), CommandStart(), state=UnverifiedState.unverified)
async def bot_start(message: types.Message):
    """Handler for /start command in private chat."""

    welcome_text = get_random_message(welcome_messages)
    await message.answer(welcome_text, reply_markup=new_user_letsgo)
    await message.delete()

# ------------------------------
# Callback Handlers for Inline Buttons
# ------------------------------

@dp.callback_query_handler(text="❌ Close", state=UnverifiedState.unverified)
async def bot_close(call: types.CallbackQuery):
    """Handler for closing the registration process."""
    await call.message.delete()

@dp.callback_query_handler(text="Let's go! 🚀", state=UnverifiedState.unverified)
async def new_user_reg(call: types.CallbackQuery):
    """Handler for starting user registration."""
    prompt = get_random_message(department_prompt_messages)
    await call.message.edit_text(prompt, reply_markup=pickup_department)
    await call.answer(cache_time=0)

@dp.callback_query_handler(text="⬅️ Back", state=UnverifiedState.unverified)
async def back_reg(call: types.CallbackQuery):
    """Handler for going back to the initial registration screen."""
    welcome_text = get_random_message(welcome_messages)
    await call.message.edit_text(welcome_text, reply_markup=new_user_letsgo)


@dp.callback_query_handler(text="Dispatch – 📋", state=UnverifiedState.unverified)
async def dispatch(call: types.CallbackQuery, state: FSMContext):
    """Handler for selecting the Dispatch department."""

    await call.message.answer(get_random_message(name_prompt_messages))
    await call.message.delete()

    # Store the selected role in the FSM context
    await state.update_data(role="Dispatcher")

    await PersonalData.realName.set()

@dp.callback_query_handler(text="Safety – 🛡️", state=UnverifiedState.unverified)
async def safety(call: types.CallbackQuery, state: FSMContext):
    """Handler for selecting the Safety department."""

    await call.message.answer(get_random_message(name_prompt_messages))
    await call.message.delete()

    # Store the selected role in the FSM context
    await state.update_data(role="Safety")

    await PersonalData.realName.set()

@dp.callback_query_handler(text="Driver – 🚛", state=UnverifiedState.unverified)
async def driver(call: types.CallbackQuery, state: FSMContext):
    """Handler for selecting the Driver department."""

    message = get_random_message(under_development_messages)
    await call.message.answer(message)
    await call.message.delete()
    # # Store the selected role in the FSM context
    # await state.update_data(role="Driver")

    # await PersonalData.realName.set()

@dp.callback_query_handler(text="Accountant – 💰️", state=UnverifiedState.unverified)
async def accounting(call: types.CallbackQuery, state: FSMContext):
    """Handler for selecting the Accounting department."""

    await call.message.answer(get_random_message(name_prompt_messages))
    await call.message.delete()

    # Store the selected role in the FSM context
    await state.update_data(role="Accounting")

    await PersonalData.realName.set()


# ------------------------------
# State Handlers for Registration
# ------------------------------

@dp.message_handler(state=PersonalData.realName)
async def answer_realName(message: types.Message, state: FSMContext):
    """Handler for validating and saving the user's full name."""
    name = message.text

    if validate_full_name(name):
        await state.update_data({"realName": name})
        await message.answer(get_random_message(dob_prompt_messages))
        await PersonalData.next()
    else:
        await message.delete()
        # Send a random name error message
        await message.answer(get_random_message(name_error_messages))

@dp.message_handler(state=PersonalData.DOB)
async def answer_dob(message: types.Message, state: FSMContext):
    """Handler for validating and saving the user's date of birth."""
    dob = message.text
    userId = message.from_user.id

    if validate_dob(dob):
        await state.update_data({"dob": dob, "userId": userId})
        await message.answer(get_random_message(phone_prompt_messages))
        await PersonalData.next()
    else:
        await message.delete()
        # Send a random date of birth error message
        await message.answer(get_random_message(dob_error_messages))

@dp.message_handler(state=PersonalData.phoneNumber)
async def answer_phone(message: types.Message, state: FSMContext):
    """Handler for validating and saving the user's phone number."""
    phone = message.text

    if validate_uzbekistan_phone(phone):
        await state.update_data({"phoneNumber": phone})

        data = await state.get_data()
        full_name = data["realName"]
        date_of_birth = data["dob"]
        phone = data["phoneNumber"]

        # Confirmation message
        msg = (
            "Here’s what you’ve entered. Give it one last look to make sure everything’s accurate before it goes to the admin for approval.\n\n"
            f"Your full name: {full_name}\n"
            f"Your date of birth: {date_of_birth}\n"
            f"Phone number: {phone}\n"
        )
        await message.answer(msg, reply_markup=admin_approval_new_user)
    else:
        await message.delete()
        # Send a random phone number error message
        await message.answer(get_random_message(phone_error_messages))

@dp.callback_query_handler(text="❌ Close", state=PersonalData.phoneNumber)
async def close_reg(call: types.CallbackQuery, state: FSMContext):
    """Handler to close the registration process when in the phone number state."""
    await call.message.delete()

# ------------------------------
# Admin Approval Process
# ------------------------------

@dp.callback_query_handler(text="✅ Send for Approval", state=PersonalData.phoneNumber)
async def send_to_admin_for_approval(call: types.CallbackQuery, state: FSMContext):
    """Sends the user's data to the admin for approval."""
    # Retrieve user data from FSM context
    data = await state.get_data()
    user_id = call.from_user.id
    full_name = data.get("realName")
    date_of_birth = data.get("dob")
    phone = data.get("phoneNumber")
    role = data.get("role")  # Retrieve the dynamic role

    # Store user data in the temporary dictionary
    temp_user_data[user_id] = {
        "user_id": user_id,
        "full_name": full_name,
        "date_of_birth": date_of_birth,
        "phone": phone,
        "role": role  # Use the dynamic role
    }

    # Prepare the message for the admin
    msg = (
        f"New User Registration Request:\n\n"
        f"Full Name: {full_name}\n"
        f"Date of Birth: {date_of_birth}\n"
        f"Phone Number: {phone}\n"
        f"Role: {role}\n\n"
        "Do you approve this registration?"
    )

    # Inline keyboard for admin's decision
    admin_buttons = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{call.from_user.id}"),
        InlineKeyboardButton("❌ Deny", callback_data=f"deny_{call.from_user.id}")
    )

    # Replace with actual admin's Telegram ID
    admin_id = 5159723225
    await bot.send_message(admin_id, msg, reply_markup=admin_buttons)

    # Notify user their information has been sent for approval
    approval_request_text = get_random_message(approval_request_messages)
    await call.message.edit_text(approval_request_text)


@dp.callback_query_handler(lambda call: call.data.startswith("approve_") or call.data.startswith("deny_"))
async def process_admin_decision(call: types.CallbackQuery):
    """Processes admin's approval or denial of the user's registration."""
    action, user_id = call.data.split("_")
    user_id = int(user_id)

    # Retrieve user data from temp_user_data
    user_data = temp_user_data.get(user_id)
    if user_data is None:
        await call.answer("User data not found. Please try again.")
        return

    if action == "approve":
        # Notify user of approval
        approval_success_text = get_random_message(approval_success_messages)
        await bot.send_message(user_id, approval_success_text)

        # Write user data to Google Sheet
        sheet = setup_google_sheets()
        add_user_to_sheet(sheet, user_data)

        # Set the user's state to the department-specific state based on their role
        role = user_data.get("role")
        if role == "Dispatcher":
            await dp.storage.set_state(chat=user_id, user=user_id, state=DispatchState.dispatch_main)
        elif role == "Safety":
            await dp.storage.set_state(chat=user_id, user=user_id, state=SafetyState.safety_main)
        elif role == "Driver":
            await dp.storage.set_state(chat=user_id, user=user_id, state=DriverState.driver_main)
        elif role == "Accounting":
            await dp.storage.set_state(chat=user_id, user=user_id, state=AccountingState.accounting_main)
        else:
            await call.answer("Invalid role specified.", show_alert=True)
            return

        # Notify the admin that the user was approved and assigned to their role-based state
        await call.answer(get_random_message(approval_sheet_messages), show_alert=True)

    elif action == "deny":
        # Notify user of denial
        denial_text = get_random_message(denial_messages)
        await bot.send_message(user_id, denial_text)

        # Place user in DeniedState.denied_main
        await dp.storage.set_state(chat=user_id, user=user_id, state=DeniedState.denied_main)

        # Write denied user data to Google Sheet with "Denied User" role
        sheet = setup_google_sheets()
        denied_user_data = user_data.copy()  # Copy original data to avoid modifying temp_user_data
        denied_user_data["role"] = "Denied User"  # Set role to "Denied User"
        add_user_to_sheet(sheet, denied_user_data)

        # Notify admin of denial
        await call.answer(get_random_message(denial_confirmation_messages), show_alert=True)

    # Optional: Clean up admin's decision message
    await call.message.delete()


@dp.message_handler(commands="new", state=PersonalData.phoneNumber)
async def finish_state(message: types.Message, state: FSMContext):
    """Handler for finishing the registration state."""
    await state.finish()
