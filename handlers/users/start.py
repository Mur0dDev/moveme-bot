# Imports
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from filters import IsPrivate
from keyboards.inline.new_user_inline_keyboard import new_user_letsgo, pickup_department
from keyboards.inline.admin_approval_new_user_reg import admin_approval_new_user
from sheet.google_sheets_integration import setup_google_sheets, add_user_to_sheet
from data.texts import text, dob_text, phone_number
from utils.misc.validators import validate_full_name, validate_dob, validate_uzbekistan_phone
from utils.misc.temp_data import temp_user_data

from loader import dp, bot
from states.dispatcher_reg_data import PersonalData

# ------------------------------
# Start Command Handler
# ------------------------------

@dp.message_handler(IsPrivate(), CommandStart())
async def bot_start(message: types.Message):
    """Handler for /start command in private chat."""
    await message.answer(text, reply_markup=new_user_letsgo)

# ------------------------------
# Callback Handlers for Inline Buttons
# ------------------------------

@dp.callback_query_handler(text="❌ Close")
async def bot_close(call: types.CallbackQuery):
    """Handler for closing the registration process."""
    await call.message.delete()

@dp.callback_query_handler(text="Let's go! 🚀")
async def new_user_reg(call: types.CallbackQuery):
    """Handler for starting user registration."""
    await call.message.edit_text("Pick your department", reply_markup=pickup_department)
    await call.answer(cache_time=0)

@dp.callback_query_handler(text="⬅️ Back")
async def back_reg(call: types.CallbackQuery):
    """Handler for going back to the initial registration screen."""
    await call.message.edit_text(text, reply_markup=new_user_letsgo)

@dp.callback_query_handler(text="Dispatch – 📋")
async def dispatch(call: types.CallbackQuery):
    """Handler for selecting the Dispatch department."""
    await call.message.delete()
    await call.message.answer("Enter your full name: ")
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
        await message.answer(dob_text)
        await PersonalData.next()
    else:
        await message.delete()
        await message.answer("Oops! That name format isn’t valid. Please enter your full name correctly.")

@dp.message_handler(state=PersonalData.DOB)
async def answer_dob(message: types.Message, state: FSMContext):
    """Handler for validating and saving the user's date of birth."""
    dob = message.text
    userId = message.from_user.id

    if validate_dob(dob):
        await state.update_data({"dob": dob, "userId": userId})
        await message.answer(phone_number)
        await PersonalData.next()
    else:
        await message.delete()
        await message.answer("Hmm, that doesn’t look like a valid date of birth. Please use the format DD/MM/YYYY.")

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
        await message.answer("Hmm, that number doesn’t seem right. Please make sure it’s correct and try again.")

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

    # Store user data in temporary dictionary
    temp_user_data[user_id] = {
        "user_id": user_id,
        "full_name": full_name,
        "date_of_birth": date_of_birth,
        "phone": phone,
        "role": "Dispatcher"
    }

    # Message for admin
    msg = (
        f"New User Registration Request:\n\n"
        f"Full Name: {full_name}\n"
        f"Date of Birth: {date_of_birth}\n"
        f"Phone Number: {phone}\n\n"
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
    await call.message.edit_text(
        "Your registration request has been sent to the admin for approval. Please wait for the response."
    )

@dp.callback_query_handler(lambda call: call.data.startswith("approve_") or call.data.startswith("deny_"))
async def process_admin_decision(call: types.CallbackQuery, state: FSMContext):
    """Processes admin's approval or denial of the user's registration."""
    # Extract user ID and decision from callback data
    action, user_id = call.data.split("_")
    user_id = int(user_id)

    # Retrieve user data
    user_data = temp_user_data.get(user_id)
    if user_data is None:
        await call.answer("User data not found. Please try again.")
        return

    if action == "approve":
        # Notify user of approval
        await bot.send_message(user_id, "✅ Your registration has been approved! Welcome to MoveMe Group.")

        # Write user data to Google Sheet
        sheet = setup_google_sheets()
        add_user_to_sheet(sheet, user_data)

        await call.answer("User approved and data written to Google Sheet.", show_alert=True)
    elif action == "deny":
        # Notify user of denial
        await bot.send_message(user_id, "❌ Your registration has been denied. Please contact support for more information.")
        await call.answer("User denied.", show_alert=True)

    await state.finish()
    await call.message.delete()  # Optional: Clean up admin's decision message

@dp.message_handler(commands="new", state=PersonalData.phoneNumber)
async def finish_state(message: types.Message, state: FSMContext):
    """Handler for finishing the registration state."""
    await state.finish()
