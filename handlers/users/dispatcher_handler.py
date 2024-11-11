# Imports
from aiogram import types
from loader import dp
from filters import IsPrivate
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher import FSMContext
from states.dispatcher_reg_data import DispatchState, SafetyState, DriverState, AccountingState, DeniedState, UnverifiedState
from sheet.google_sheets_integration import setup_google_sheets, get_user_role_by_telegram_id, get_full_name_by_user_id
from keyboards.inline.new_user_inline_keyboard import new_user_letsgo
from data.dispatcher_texts import get_random_greeting, truck_status_under_development_messages
from data.texts import get_random_message, welcome_messages
from keyboards.inline.dispatcher_inline_keyboards import dispatcher_main_features, dispatcher_start_over


@dp.message_handler(IsPrivate(), commands=['start', 'help'])
async def verify_user_role(message: types.Message):
    """Verify user's role from Google Sheets and assign the appropriate state."""

    telegram_id = message.from_user.id
    sheet = setup_google_sheets()

    # Retrieve the role from the Google Sheet
    user_role = get_user_role_by_telegram_id(sheet, telegram_id)

    if user_role == "Dispatcher":
        await DispatchState.dispatch_main.set()
        # Get the user's Telegram ID
        user_id = message.from_user.id

        # Retrieve the full name from Google Sheets based on user_id
        full_name = get_full_name_by_user_id(user_id)

        await message.delete()
        await message.answer(get_random_greeting(full_name), reply_markup=dispatcher_main_features)

    elif user_role == "Safety":
        await SafetyState.safety_main.set()
        await message.answer("Welcome to the Safety team!")

    elif user_role == "Driver":
        await DriverState.driver_main.set()
        await message.answer("Welcome, Driver! You’re ready to roll.")

    elif user_role == "Accounting":
        await AccountingState.accounting_main.set()
        await message.answer("Welcome to the Accounting department.")

    elif user_role == "Denied User":
        await DeniedState.denied_main.set()
        await message.answer("Your access has been denied. Contact support if you think this is an error.")

    else:
        # If user is not found in the sheet
        await UnverifiedState.unverified.set()
        welcome_text = get_random_message(welcome_messages)
        await message.answer(welcome_text, reply_markup=new_user_letsgo)


@dp.message_handler(IsPrivate(), CommandStart(), state=DispatchState.dispatch_main)
async def dispatcher_main(message: types.Message):
    """Main menu for dispatcher-specific features."""
    # Get the user's Telegram ID
    user_id = message.from_user.id

    # Retrieve the full name from Google Sheets based on user_id
    full_name = get_full_name_by_user_id(user_id)
    await message.delete()
    await message.answer(get_random_greeting(full_name), reply_markup=dispatcher_main_features)

@dp.callback_query_handler(text="🛠️ Load Assign", state=DispatchState.dispatch_main)
async def handle_assign_load(call: types.CallbackQuery):
    await call.answer("Assign Load feature selected.")
    # Add further handling here

@dp.callback_query_handler(text="🔍 Truck Status Check", state=DispatchState.dispatch_main)
async def handle_truck_status(call: types.CallbackQuery):
    # Respond with an "under development" message
    message = get_random_message(truck_status_under_development_messages)
    await call.message.edit_text(message, reply_markup=dispatcher_start_over)
    await call.answer("Truck Status feature selected.")


# @dp.callback_query_handler(text="truck_status", state=DispatchState.dispatch_main)
# async def handle_truck_status(call: types.CallbackQuery):
#     # Respond with an "under development" message
#     msg = get_random_message(truck_status_under_development_messages)
#     await call.message.edit_text(msg, reply_markup=dispatcher_start_over)
#     await call.answer("Truck Status feature selected.")
#     # Add further handling here

@dp.callback_query_handler(text="Start Over", state=DispatchState.dispatch_main)
async def handle_start_over(call: types.CallbackQuery):
    # Get the user's Telegram ID
    user_id = call.from_user.id

    # Retrieve the full name from Google Sheets based on user_id
    full_name = get_full_name_by_user_id(user_id)
    await call.message.edit_text(get_random_greeting(full_name), reply_markup=dispatcher_main_features)
    await call.answer("Start Over selected.")

@dp.callback_query_handler(text="🔚 End and Close", state=DispatchState.dispatch_main)
async def handle_close(call: types.CallbackQuery):
    await call.message.delete()
    await call.answer("Closing the dispatcher menu.")
    # Add further handling here




