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
from keyboards.inline.dispatcher_inline_keyboards import dispatcher_main_features, dispatcher_start_over, team_or_solo_driver
from states.assign_load_states import AssignLoad
from utils.misc.validators import validate_full_name
from utils.misc.load_assignment_validations import validate_truck_number, validate_load_number, validate_broker_name


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

# ====== BEGIN: Assign Load Feature (Dispatcher) ======
# ====== BEGIN: Assign Load Feature (Dispatcher) ======
# ====== BEGIN: Assign Load Feature (Dispatcher) ======


@dp.callback_query_handler(text="🛠️ Load Assign", state=DispatchState.dispatch_main)
async def handle_assign_load(call: types.CallbackQuery):
    await call.answer("Assign Load feature selected.")
    await call.message.answer("Please enter the Driver Name:")
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
    truck_number_format_warn_message = (
        f"Please enter the Truck Number. It should be in one of the following formats:\n\n"
        f"Only numbers (e.g., 1234)\n"
        f"One letter at the beginning or end, followed by numbers (e.g., A1234 or 1234B)\n\n"
        f"Make sure to follow these guidelines to proceed."
    )
    await message.answer(truck_number_format_warn_message)
    await AssignLoad.truck_number.set()

# Handler for Truck Number input with validation
@dp.message_handler(state=AssignLoad.truck_number)
async def enter_truck_number(message: types.Message, state: FSMContext):
    truck_number = message.text
    if not validate_truck_number(truck_number):
        await message.answer("Invalid truck number format. Please enter a valid Truck Number (e.g., A1234 or 1234B).")
        return
    await state.update_data(truck_number=truck_number)
    await message.answer("Please enter the Load Number:")
    await AssignLoad.load_number.set()

# Handler for Load Number input
@dp.message_handler(state=AssignLoad.load_number)
async def enter_load_number(message: types.Message, state: FSMContext):
    load_number = message.text
    if not validate_load_number(load_number):
        await message.answer("Invalid load number format. Please enter a valid Load Number (only letters and numbers, no symbols).")
        return
    await state.update_data(load_number=load_number)
    await message.answer("Please enter the Broker Name:")
    await AssignLoad.broker_name.set()

# Handler for Broker Name input with validation
@dp.message_handler(state=AssignLoad.broker_name)
async def enter_broker_name(message: types.Message, state: FSMContext):
    broker_name = message.text
    if not validate_broker_name(broker_name):
        await message.answer("Invalid broker name format. Please enter a valid Broker Name (only letters and spaces, no numbers or symbols).")
        return
    await state.update_data(broker_name=broker_name)
    await message.answer("Is this a Team or Solo load? Please type:\n\n👥 Team\n👤 Solo", reply_markup=validate_broker_name)
    await AssignLoad.team_or_solo.set()




# ====== END: Assign Load Feature (Dispatcher) ======
# ====== END: Assign Load Feature (Dispatcher) ======
# ====== END: Assign Load Feature (Dispatcher) ======


@dp.callback_query_handler(text="🔍 Truck Status Check", state=DispatchState.dispatch_main)
async def handle_truck_status(call: types.CallbackQuery):

    await call.answer("Truck Status feature selected.")
    # Respond with an "under development" message
    message = get_random_message(truck_status_under_development_messages)
    await call.message.edit_text(message, reply_markup=dispatcher_start_over)


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




