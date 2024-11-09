import re
from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from filters import IsPrivate
from keyboards.inline.new_user_inline_keyboard import new_user_letsgo, pickup_department
from keyboards.inline.admin_approval_new_user_reg import admin_approval_new_user
from sheet.google_sheets_integration import setup_google_sheets, add_user_to_sheet

from loader import dp, bot
from states.dispatcher_reg_data import PersonalData

# Global text variable
text = "💼 Welcome to the MoveMe Group family! \nWe're so glad you're here. 🥳\n\n"
text += "If you're already part of our amazing team,\nlet's get you registered in just a few steps:\n\n"
text += "1️⃣ Pick your department\n"
text += "2️⃣ Enter your details (don’t worry, we’ll guide you!)\n"
text += "3️⃣ Click 'Confirm' to join the team chat!\n\n"
text += "When you're set, just tap below to get started! 👇"

# Global dob_text variable
dob_text = f"Enter your date of birth:\n"
dob_text += f"use the DD/MM/YYYY format"

# Global phone_number variable
phone_number = "Enter your Uzb phone number:\n"
phone_number += "use the format +998 XX XXX XXXX "

# Global temporary dictionary to store user data
temp_user_data = {}

# Regular expression for validating full names
full_name_pattern = re.compile(r"^[A-Z][a-z]*([-'\s][A-Z][a-z]*)*$")

# Regular expression to match DD/MM/YYYY format within the range of 1970 to 2010
dob_pattern = re.compile(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(19[7-9][0-9]|200[0-9]|2010)$")

# Regular expression for Uzbekistan phone numbers
uzbekistan_phone_pattern = re.compile(r"^(?:\+998|998)(?:[0-9]{2})\s?[0-9]{3}\s?[0-9]{4}$")


@dp.message_handler(IsPrivate(), CommandStart())
async def bot_start(message: types.Message):
    await message.answer(text, reply_markup=new_user_letsgo)

@dp.callback_query_handler(text = "❌ Close")
async def bot_close(call: types.CallbackQuery):
    await call.message.delete()

@dp.callback_query_handler(text = "Let's go! 🚀")
async def new_user_reg(call: types.CallbackQuery):
    await call.message.edit_text("Pick your department", reply_markup=pickup_department)
    # await call.message.edit_reply_markup(reply_markup=pickup_department)
    await call.answer(cache_time=0)

@dp.callback_query_handler(text = "⬅️ Back")
async def back_reg(call: types.CallbackQuery):
    await call.message.edit_text(text, reply_markup=new_user_letsgo)

@dp.callback_query_handler(text = "Dispatch – 📋")
async def dispatch(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("Enter your full name: ")
    await PersonalData.realName.set()

@dp.message_handler(state=PersonalData.realName)
async def answer_realName(message: types.Message, state: FSMContext):
    name = message.text

    def validate_full_name(name):
        return bool(full_name_pattern.match(name))

    if validate_full_name(name):
        await state.update_data(
            {"realName": name}
        )
        await message.answer(dob_text)
        await PersonalData.next()

    else:
        await message.delete()
        await message.answer("Oops! That name format isn’t valid. Please enter your full name correctly.")

@dp.message_handler(state=PersonalData.DOB)
async def answer_dob(message: types.Message, state: FSMContext):
    dob = message.text
    userId = message.from_user.id

    def validate_dob(dob):
        # First, check the format and year range with regex
        if not dob_pattern.match(dob):
            return False

        # Then, validate the date using datetime and ensure it’s within the desired range
        try:
            dob_date = datetime.strptime(dob, "%d/%m/%Y")
            # Check if the date is between 01/01/1970 and 31/12/2010
            return datetime(1970, 1, 1) <= dob_date <= datetime(2010, 12, 31)
        except ValueError:
            return False

    if validate_dob(dob):
        await state.update_data(
            {
                "dob": dob,
                "userId": userId
            }
        )
        await message.answer(phone_number)
        await PersonalData.next()
    else:
        await message.delete()
        await message.answer("Hmm, that doesn’t look like a valid date of birth. Please use the format DD/MM/YYYY.")

@dp.message_handler(state=PersonalData.phoneNumber)
async def answer_phone(message: types.Message, state: FSMContext):
    phone = message.text

    def validate_uzbekistan_phone(phone):
        return bool(uzbekistan_phone_pattern.match(phone))

    if validate_uzbekistan_phone(phone):
        await state.update_data(
            {"phoneNumber": phone}
        )

        data = await state.get_data()
        full_name = data["realName"]
        date_of_birth = data["dob"]
        phone = data["phoneNumber"]

        msg = "Here’s what you’ve entered. Give it one last look to make sure everything’s accurate before it goes to the admin for approval.\n\n"
        msg += f"Your full name: {full_name}\n"
        msg += f"Your date of birth: {date_of_birth}\n"
        msg += f"Phone number: {phone}\n"
        await message.answer(msg, reply_markup=admin_approval_new_user)


    else:
        await message.delete()
        await message.answer("Hmm, that number doesn’t seem right. Please make sure it’s correct and try again.")

@dp.callback_query_handler(text = "❌ Close", state=PersonalData.phoneNumber)
async def close_reg(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    # await state.finish()

# Function to send data to admin for approval
@dp.callback_query_handler(text = "✅ Send for Approval", state=PersonalData.phoneNumber)
async def send_to_admin_for_approval(call: types.CallbackQuery, state: FSMContext):
    # Retrieve user data from FSM context
    data = await state.get_data()
    user_id = call.from_user.id
    full_name = data.get("realName")
    date_of_birth = data.get("dob")
    phone = data.get("phoneNumber")

    # Store user data in the temporary dictionary
    temp_user_data[user_id] = {
        "user_id": user_id,
        "full_name": full_name,
        "date_of_birth": date_of_birth,
        "phone": phone,
        "role": "Dispatcher"
    }
    # Prepare the message for the admin
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
    # Send message to admin
    await bot.send_message(admin_id, msg, reply_markup=admin_buttons)

    # Notify user that their information has been sent to the admin
    await call.message.edit_text(
        "Your registration request has been sent to the admin for approval. Please wait for the response.")


# Callback handler for admin approval or denial
@dp.callback_query_handler(lambda call: call.data.startswith("approve_") or call.data.startswith("deny_"))
async def process_admin_decision(call: types.CallbackQuery, state: FSMContext):
    # Extract user ID and decision from callback data
    action, user_id = call.data.split("_")
    user_id = int(user_id)  # Convert to integer

    # Retrieve user data from the temporary dictionary
    user_data = temp_user_data.get(user_id)
    if user_data is None:
        await call.answer("User data not found. Please try again.")
        return

    if action == "approve":
        # Notify the user of approval
        await bot.send_message(user_id, "✅ Your registration has been approved! Welcome to MoveMe Group.")

        # Write user data to Google Sheet
        sheet = setup_google_sheets()
        add_user_to_sheet(sheet, user_data)

        await call.answer("User approved and data written to Google Sheet.", show_alert=True)

    elif action == "deny":
        # Notify the user of denial
        await bot.send_message(user_id,
                               "❌ Your registration has been denied. Please contact support for more information.")
        await call.answer("User denied.", show_alert=True)

    # Finish the user's state now that the admin has made a decision
    await state.finish()

    # Delete the admin's decision message to keep the chat clean (optional)
    await call.message.delete()

@dp.message_handler(commands="new", state=PersonalData.phoneNumber)
async def finish_state(message: types.Message, state: FSMContext):
    command = message.text
    await state.finish()
