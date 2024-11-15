# Imports
from aiogram import types
from loader import dp
from filters import IsPrivate
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from states.dispatcher_reg_data import DispatchState, SafetyState, DriverState, AccountingState, DeniedState, UnverifiedState
from sheet.google_sheets_integration import setup_google_sheets, get_user_role_by_telegram_id, get_full_name_by_user_id
from keyboards.inline.new_user_inline_keyboard import new_user_letsgo
from data.dispatcher_texts import get_random_greeting, truck_status_under_development_messages
from data.texts import get_random_message, welcome_messages
from keyboards.inline.dispatcher_inline_keyboards import dispatcher_main_features, dispatcher_start_over, team_or_solo_driver, pickup_datetime_options, delivery_datetime_options, confirmation_options
from states.assign_load_states import AssignLoad
from utils.misc.validators import validate_full_name
from utils.misc.load_assignment_validations import validate_truck_number, validate_load_number, validate_broker_name, validate_location,validate_datetime_us, validate_datetime_range_us, validate_loaded_miles


@dp.message_handler(IsPrivate(), commands=['start', 'help'])
async def verify_user_role(message: types.Message):
    """Verify user's role from cached data and assign the appropriate state."""

    telegram_id = message.from_user.id

    # Retrieve the role from the cache
    user_role = get_user_role_by_telegram_id(telegram_id)  # Remove 'sheet' argument

    if user_role == "Dispatcher":
        await DispatchState.dispatch_main.set()
        # Retrieve the full name from the cache based on user_id
        full_name = get_full_name_by_user_id(telegram_id)

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
        # If user is not found in the cache
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
    await message.answer("Is this a Team or Solo load? Please type:\n\n👥 Team\n👤 Solo", reply_markup=team_or_solo_driver)
    await AssignLoad.team_or_solo.set()

# Callback handler for Team selection
@dp.callback_query_handler(text="team", state=AssignLoad.team_or_solo)
async def team_selected(call: CallbackQuery, state: FSMContext):
    await state.update_data(team_or_solo="Team")
    await call.message.answer("Please enter the Pickup Location:")
    await AssignLoad.pickup_location.set()
    await call.answer()  # Acknowledge the callback to remove loading state on the button

# Callback handler for Solo selection
@dp.callback_query_handler(text="solo", state=AssignLoad.team_or_solo)
async def solo_selected(call: CallbackQuery, state: FSMContext):
    await state.update_data(team_or_solo="Solo")
    await call.message.answer("Please enter the Pickup Location:")
    await AssignLoad.pickup_location.set()
    await call.answer()  # Acknowledge the callback to remove loading state on the button

# Handler for Pickup Location input with validation
@dp.message_handler(state=AssignLoad.pickup_location)
async def enter_pickup_location(message: types.Message, state: FSMContext):
    pickup_location = message.text
    if not validate_location(pickup_location):
        await message.answer("Invalid location format. Please enter a valid location, including ZIP code (e.g., '123 Main St, City, State, 12345').")
        return
    await state.update_data(pickup_location=pickup_location)
    await message.answer("Please enter the Pickup Date & Time (e.g., YYYY-MM-DD HH:MM):", reply_markup=pickup_datetime_options)
    await AssignLoad.pickup_datetime.set()

# Callback handler for Appointment Date & Time
@dp.callback_query_handler(text="appointment_datetime", state=AssignLoad.pickup_datetime)
async def select_appointment_datetime(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Please enter the Appointment Date & Time (e.g., MM/DD/YYYY HH:MM):")
    await state.update_data(datetime_type="appointment")
    await AssignLoad.pickup_datetime.set()
    await call.answer()

# Callback handler for Date & Time (Range Possible)
@dp.callback_query_handler(text="datetime_range", state=AssignLoad.pickup_datetime)
async def select_datetime_range(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Please enter the Pickup Date & Time range (e.g., MM/DD/YYYY HH:MM - HH:MM):")
    await state.update_data(datetime_type="range")
    await AssignLoad.pickup_datetime.set()
    await call.answer()

# Callback handler for First Come First Serve (FCFS)
@dp.callback_query_handler(text="fcfs", state=AssignLoad.pickup_datetime)
async def select_fcfs(call: CallbackQuery, state: FSMContext):
    await state.update_data(datetime_type="fcfs", pickup_datetime="First Come First Serve")
    await call.message.answer("Please enter the Delivery Location:")
    await AssignLoad.delivery_location.set()
    await call.answer()

# Unified handler for Pickup Date & Time input based on dispatcher selection
@dp.message_handler(state=AssignLoad.pickup_datetime)
async def enter_pickup_datetime(message: types.Message, state: FSMContext):
    # Retrieve the datetime type selected by the dispatcher
    data = await state.get_data()
    datetime_type = data.get("datetime_type")
    pickup_datetime_input = message.text

    if datetime_type == "appointment":
        # Appointment Date & Time: Validate single datetime format
        if not validate_datetime_us(pickup_datetime_input):
            await message.answer("Invalid format. Please enter the Appointment Date & Time in the format: MM/DD/YYYY HH:MM")
            return
        await state.update_data(pickup_datetime=pickup_datetime_input)

    elif datetime_type == "range":
        # Date & Time (Range Possible): Validate either single datetime or datetime range
        if not (validate_datetime_us(pickup_datetime_input) or validate_datetime_range_us(pickup_datetime_input)):
            await message.answer("Invalid format. Please enter the Pickup Date & Time in one of the following formats:\n"
                                 "- Single: MM/DD/YYYY HH:MM\n"
                                 "- Range: MM/DD/YYYY HH:MM - HH:MM")
            return
        await state.update_data(pickup_datetime=pickup_datetime_input)

    elif datetime_type == "fcfs":
        # First Come First Serve: Automatically set value without validation
        await state.update_data(pickup_datetime="First Come First Serve")

    # Proceed to the next step after setting pickup_datetime
    await message.answer("Please enter the Delivery Location:")
    await AssignLoad.delivery_location.set()

@dp.message_handler(state=AssignLoad.delivery_location)
async def enter_delivery_location(message: types.Message, state: FSMContext):
    delivery_location = message.text

    # Validate the delivery location format
    if not validate_location(delivery_location):
        await message.answer(
            "Invalid location format. Please enter a valid delivery location including ZIP code "
            "(e.g., '123 Main St, City, State, 12345')."
        )
        return  # Stops here if the location is invalid, allowing the dispatcher to retry

    # If valid, store the location and proceed to the next step
    await state.update_data(delivery_location=delivery_location)
    await message.answer("Please enter the Delivery Date & Time (e.g., MM/DD/YYYY HH:MM):", reply_markup=delivery_datetime_options)
    await AssignLoad.delivery_datetime.set()

@dp.callback_query_handler(text="delivery_appointment_datetime", state=AssignLoad.delivery_datetime)
async def select_delivery_appointment_datetime(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Please enter the Delivery Appointment Date & Time (e.g., MM/DD/YYYY HH:MM):")
    await state.update_data(datetime_type="appointment")
    await AssignLoad.delivery_datetime.set()
    await call.answer()

@dp.callback_query_handler(text="delivery_datetime_range", state=AssignLoad.delivery_datetime)
async def select_delivery_datetime_range(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Please enter the Delivery Date & Time range (e.g., MM/DD/YYYY HH:MM - HH:MM):")
    await state.update_data(datetime_type="range")
    await AssignLoad.delivery_datetime.set()
    await call.answer()

@dp.callback_query_handler(text="delivery_fcfs", state=AssignLoad.delivery_datetime)
async def select_delivery_fcfs(call: CallbackQuery, state: FSMContext):
    await state.update_data(datetime_type="fcfs", delivery_datetime="First Come First Serve")
    await call.message.answer("Please enter the Loaded Miles:")
    await AssignLoad.loaded_miles.set()
    await call.answer()

@dp.message_handler(state=AssignLoad.delivery_datetime)
async def enter_delivery_datetime(message: types.Message, state: FSMContext):
    # Retrieve the datetime type selected by the dispatcher
    data = await state.get_data()
    datetime_type = data.get("datetime_type")
    delivery_datetime_input = message.text

    if datetime_type == "appointment":
        # Appointment Date & Time: Validate single datetime format
        if not validate_datetime_us(delivery_datetime_input):
            await message.answer("Invalid format. Please enter the Delivery Date & Time in the format: MM/DD/YYYY HH:MM")
            return
        await state.update_data(delivery_datetime=delivery_datetime_input)

    elif datetime_type == "range":
        # Date & Time (Range Possible): Validate either single datetime or datetime range
        if not (validate_datetime_us(delivery_datetime_input) or validate_datetime_range_us(delivery_datetime_input)):
            await message.answer("Invalid format. Please enter the Delivery Date & Time in one of the following formats:\n"
                                 "- Single: MM/DD/YYYY HH:MM\n"
                                 "- Range: MM/DD/YYYY HH:MM - HH:MM")
            return
        await state.update_data(delivery_datetime=delivery_datetime_input)

    elif datetime_type == "fcfs":
        # First Come First Serve: Automatically set value without validation
        await state.update_data(delivery_datetime="First Come First Serve")

    # Proceed to the next step after setting delivery_datetime
    await message.answer("Please enter the Loaded Miles:")
    await AssignLoad.loaded_miles.set()

@dp.message_handler(state=AssignLoad.loaded_miles)
async def enter_loaded_miles(message: types.Message, state: FSMContext):
    loaded_miles = message.text

    # Validate loaded miles using the regular expression
    if not validate_loaded_miles(loaded_miles):
        await message.answer("Invalid input. Please enter a positive numerical value for Loaded Miles (e.g., 100 or 100.5).")
        return

    # Convert to float for precision and update state
    await state.update_data(loaded_miles=float(loaded_miles))
    await message.answer("Please enter the Deadhead Miles:")
    await AssignLoad.deadhead_miles.set()

@dp.message_handler(state=AssignLoad.deadhead_miles)
async def enter_deadhead_miles(message: types.Message, state: FSMContext):
    deadhead_miles = message.text

    # Validate deadhead miles using the regular expression
    if not validate_loaded_miles(deadhead_miles):  # Reusing validate_loaded_miles for similar validation
        await message.answer("Invalid input. Please enter a positive numerical value for Deadhead Miles (e.g., 50 or 50.5).")
        return

    # Convert to float for precision and update state
    await state.update_data(deadhead_miles=float(deadhead_miles))
    await message.answer("Please enter the Trip Rate:")
    await AssignLoad.load_rate.set()

@dp.message_handler(state=AssignLoad.load_rate)
async def enter_load_rate(message: types.Message, state: FSMContext):
    load_rate = message.text

    # Validate load rate using the regular expression
    if not validate_loaded_miles(load_rate):  # Reusing validate_loaded_miles for similar validation
        await message.answer("Invalid input. Please enter a positive numerical value for Load Rate (e.g., 1500 or 1500.75).")
        return

    # Convert to float for precision and update state
    await state.update_data(load_rate=float(load_rate))

    # Retrieve all entered data from state
    data = await state.get_data()

    # Format the summary of load details
    summary = (
        f"**Load Assignment Summary**\n"
        f"Driver Name: {data.get('driver_name')}\n"
        f"Truck Number: {data.get('truck_number')}\n"
        f"Load Number: {data.get('load_number')}\n"
        f"Broker Name: {data.get('broker_name')}\n"
        f"Load Type: {data.get('team_or_solo')}\n"
        f"Pickup Location: {data.get('pickup_location')}\n"
        f"Pickup Date & Time: {data.get('pickup_datetime')}\n"
        f"Delivery Location: {data.get('delivery_location')}\n"
        f"Delivery Date & Time: {data.get('delivery_datetime')}\n"
        f"Loaded Miles: {data.get('loaded_miles')}\n"
        f"Deadhead Miles: {data.get('deadhead_miles')}\n"
        f"Load Rate: {data.get('load_rate')}\n"
    )

    await message.answer(summary + "\n\nReview your load details and confirm to submit or edit.", reply_markup=confirmation_options)
    await AssignLoad.confirmation.set()




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
