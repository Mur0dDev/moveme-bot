# Imports
import logging
from aiogram import types
from loader import dp
from filters import IsPrivate
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from states.dispatcher_reg_data import DispatchState, SafetyState, DriverState, AccountingState, DeniedState, UnverifiedState
from sheet.google_sheets_integration import get_user_role_by_telegram_id, get_full_name_by_user_id, search_truck_details, append_load_assignment_data
from keyboards.inline.new_user_inline_keyboard import new_user_letsgo
from data.dispatcher_texts import get_random_greeting, truck_status_under_development_messages
from data.texts import get_random_message, welcome_messages
from keyboards.inline.dispatcher_inline_keyboards import dispatcher_main_features, dispatcher_start_over, team_or_solo_driver, pickup_datetime_options, delivery_datetime_options, confirmation_options
from states.assign_load_states import AssignLoad
from utils.misc.load_assignment_validations import validate_load_number, validate_broker_name, validate_location, validate_datetime_us, validate_datetime_range_us, validate_loaded_miles


@dp.message_handler(IsPrivate(), commands=['start', 'help'])
async def verify_user_role(message: types.Message):
    """Verify user's role from cached data and assign the appropriate state."""
    telegram_id = message.from_user.id

    # Retrieve the role from the cache
    user_role = get_user_role_by_telegram_id(telegram_id)

    if user_role == "Dispatcher":
        await DispatchState.dispatch_main.set()
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
async def dispatcher_main(message: types.Message, state: FSMContext):
    """
    Main menu for dispatcher-specific features.
    """
    # Get the user's Telegram ID
    user_id = message.from_user.id

    # Retrieve the full name from Google Sheets based on user_id
    full_name = get_full_name_by_user_id(user_id)

    # Save the dispatcher name in FSM state
    await state.update_data(dispatcher_name=full_name)

    await message.delete()
    await message.answer(get_random_greeting(full_name), reply_markup=dispatcher_main_features)


# Assign Load Workflow
@dp.callback_query_handler(text="🛠️ Load Assign", state=DispatchState.dispatch_main)
async def handle_assign_load(call: types.CallbackQuery, state: FSMContext):
    # Retrieve dispatcher name from the state to keep track throughout the flow
    data = await state.get_data()
    dispatcher_name = data.get('dispatcher_name')

    if not dispatcher_name:
        user_id = call.from_user.id
        dispatcher_name = get_full_name_by_user_id(user_id)
        await state.update_data(dispatcher_name=dispatcher_name)

    await call.message.edit_text("🛠️ Load Assignment:\nReady to assign a new load! Let's begin.\n\n"
                              "🚛 Step 1: Please provide the Truck Number to search for available trucks.")

    await AssignLoad.truck_number.set()


@dp.message_handler(state=AssignLoad.truck_number)
async def search_and_select_truck_number(message: types.Message, state: FSMContext):
    truck_number = message.text

    # Search for trucks
    matched_trucks = search_truck_details(truck_number)

    if not matched_trucks:
        await message.answer(f"❌ No Matches Found:\n\nWe couldn’t find any trucks matching '{truck_number}'. Please double-check and try again.")
        return

    # Save matched trucks and the original truck number to FSMContext
    await state.update_data(matched_trucks=matched_trucks, searched_truck_number=truck_number)

    # Create a numbered list of results
    results_message = "🔎 Search Results:\nHere are the trucks matching your query:\n\n"
    for idx, truck in enumerate(matched_trucks, start=1):
        results_message += (
            f"🔎 Search Result  {idx}:\n"
            f"🚛 Truck Number:  {truck['Truck Number']}\n"
            f"🏢 Company Name:  {truck['Company Name']}\n"
            f"👨‍✈️ Driver Name:  {truck['Driver Name']}\n"
            f"👥 Group Name:  {truck['Group Name']}\n\n"
        )

    # Generate inline buttons for selecting a result
    truck_buttons = InlineKeyboardMarkup(row_width=5)
    for idx in range(1, len(matched_trucks) + 1):
        truck_buttons.insert(InlineKeyboardButton(
            text=str(idx),
            callback_data=f"select_truck:{idx}"
        ))

    # Add cancel button
    truck_buttons.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_selection"))

    await message.answer(results_message, reply_markup=truck_buttons)


@dp.callback_query_handler(Text(startswith="select_truck:"), state=AssignLoad.truck_number)
async def handle_truck_selection(call: types.CallbackQuery, state: FSMContext):
    _, selected_index = call.data.split(":")
    selected_index = int(selected_index) - 1  # Convert to zero-based index

    # Retrieve matched trucks from FSMContext
    data = await state.get_data()
    matched_trucks = data.get("matched_trucks")

    if not matched_trucks or selected_index < 0 or selected_index >= len(matched_trucks):
        await call.answer("🚫 Hmm, that doesn’t look like a valid choice. No worries, give it another shot!", show_alert=True)
        return

    selected_truck = matched_trucks[selected_index]

    # Update FSM state with selected truck details
    await state.update_data(
        truck_number=selected_truck['Truck Number'],
        company_name=selected_truck['Company Name'],
        driver_name=selected_truck['Driver Name'],
        group_name=selected_truck['Group Name'],
        group_id=selected_truck.get('Group ID')  #Ensure Group ID is included
    )

    await call.message.edit_text(
        f"🚛 Truck Selection Successful!\n\n"
        f"Here are the details of your selected truck:\n"
        f"🚛 Truck Number: {selected_truck['Truck Number']}\n"
        f"🏢 Company Name: {selected_truck['Company Name']}\n"
        f"👨‍✈️ Driver Name: {selected_truck['Driver Name']}\n\n"
        f"🎯 Great choice! Now, let’s move forward.\n"
        f"📋 Please provide the load number."
    )
    await AssignLoad.load_number.set()  # Move to the next step
    await call.answer()


@dp.callback_query_handler(Text(equals="cancel_selection"), state=AssignLoad.truck_number)
async def cancel_truck_selection(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(f"🚫 Truck Selection Canceled!\n\n"
                              f"No worries, you can start fresh now.\n"
                              f"🔄 Simply type /start to begin again.")
    await DispatchState.dispatch_main.set()
    await call.answer()


# Handler for Load Number input
@dp.message_handler(state=AssignLoad.load_number)
async def enter_load_number(message: types.Message, state: FSMContext):
    load_number = message.text
    if not validate_load_number(load_number):
        await message.answer(f"❌ Invalid Load Number Format.\n\n"
                             f"The load number should contain only letters and numbers, without any symbols.\n\n"
                             f"🔄 Please re-enter the load number.")
        return
    await state.update_data(load_number=load_number)
    await message.answer(f"📋 What's the Broker's Name?\n\n"
                         f"Enter the name of the broker managing this load.\n\n"
                         f"✅ Use only letters and spaces to ensure accuracy.")
    await AssignLoad.broker_name.set()

# Handler for Broker Name input with validation
@dp.message_handler(state=AssignLoad.broker_name)
async def enter_broker_name(message: types.Message, state: FSMContext):
    broker_name = message.text
    if not validate_broker_name(broker_name):
        await message.answer(f"📛 Oops, That's Not Right!\n\n"
                             f"The broker name should only include letters and spaces.\n\n"
                             f"Please double-check and try again.")
        return
    await state.update_data(broker_name=broker_name)
    await message.answer(f"🚛 Load Type Selection\n\n"
                         f"Is this a Team load (multiple drivers) or a Solo load (one driver)?\n"
                         f"Type your choice:\n\n"
                         f"-- 👥 Team\n"
                         f"-- 👤 Solo", reply_markup=team_or_solo_driver)
    await AssignLoad.team_or_solo.set()

# Callback handler for Team selection
@dp.callback_query_handler(text="team", state=AssignLoad.team_or_solo)
async def team_selected(call: CallbackQuery, state: FSMContext):
    await state.update_data(team_or_solo="Team")
    await call.message.edit_text(f"🗺️ Provide the Pickup Location\n\n"
                              f"Enter the full address for the pickup, including:\n"
                              f"-- Street Address\n"
                              f"-- City, State\n"
                              f"-- ZIP Code\n\n"
                              f"Example: \"123 Main St, City, State, 12345\"")
    await AssignLoad.pickup_location.set()
    await call.answer()  # Acknowledge the callback to remove loading state on the button

# Callback handler for Solo selection
@dp.callback_query_handler(text="solo", state=AssignLoad.team_or_solo)
async def solo_selected(call: CallbackQuery, state: FSMContext):
    await state.update_data(team_or_solo="Solo")
    await call.message.edit_text(f"📍 Pickup Location Required\n\n"
                              f"Please enter the Pickup Location, including:\n"
                              f"-- Street Address\n"
                              f"-- City, State\n"
                              f"-- ZIP Code\n\n"
                              f"Example: \"123 Main St, City, State, 12345\"")
    await AssignLoad.pickup_location.set()
    await call.answer()  # Acknowledge the callback to remove loading state on the button

# Handler for Pickup Location input with validation
@dp.message_handler(state=AssignLoad.pickup_location)
async def enter_pickup_location(message: types.Message, state: FSMContext):
    pickup_location = message.text
    if not validate_location(pickup_location):
        await message.answer(f"⚠️ Invalid Location\n\n"
                              f"Ensure the location includes:\n"
                              f"-- Street Address\n"
                              f"-- City, State\n"
                              f"-- ZIP Code\n\n"
                              f"Example: \"123 Main St, City, State, 12345\"")
        return
    await state.update_data(pickup_location=pickup_location)
    await message.answer(f"🗓️ Select the Pickup Date & Time Type:\n\n"
                         f"-- Appointment Date & Time: Specify exact date and time.\n"
                         f"-- Date & Time (Range Possible): Provide a time range.\n"
                         f"-- First Come First Serve: No specific appointment required", reply_markup=pickup_datetime_options)
    await AssignLoad.pickup_datetime.set()

# Callback handler for Appointment Date & Time
@dp.callback_query_handler(text="appointment_datetime", state=AssignLoad.pickup_datetime)
async def select_appointment_datetime(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"📅 Enter the Appointment Date & Time\n\n"
                                 f"💡 Example: MM/DD/YYYY HH:MM\n\n"
                                 f"Ensure the format is correct to proceed.")
    await state.update_data(datetime_type="appointment")
    await AssignLoad.pickup_datetime.set()
    await call.answer()

# Callback handler for Date & Time (Range Possible)
@dp.callback_query_handler(text="datetime_range", state=AssignLoad.pickup_datetime)
async def select_datetime_range(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"⏰ Enter the Pickup Date & Time Range\n\n"
                                 f"📌 Format: MM/DD/YYYY HH:MM - HH:MM\n\n"
                                 f"Ensure the format is correct to avoid delays.")
    await state.update_data(datetime_type="range")
    await AssignLoad.pickup_datetime.set()
    await call.answer()

# Callback handler for First Come First Serve (FCFS)
@dp.callback_query_handler(text="fcfs", state=AssignLoad.pickup_datetime)
async def select_fcfs(call: CallbackQuery, state: FSMContext):
    await state.update_data(datetime_type="fcfs", pickup_datetime="First Come First Serve")
    await call.message.edit_text(f"📍 Enter the Delivery Location\n\n"
                                 f"💡 Example: 123 Main St, City, State, ZIP Code\n\n"
                                 f"Please ensure the format is correct to avoid delays.")
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
            await message.answer(f"⚠️ Error: Invalid Format\n\n"
                                 f"✅ Ensure the Appointment Date & Time follows this format:\n"
                                 f"🕒 MM/DD/YYYY HH:MM\n\n"
                                 f"Example: 01/01/2024 10:00")
            return
        await state.update_data(pickup_datetime=pickup_datetime_input)

    elif datetime_type == "range":
        # Date & Time (Range Possible): Validate either single datetime or datetime range
        if not (validate_datetime_us(pickup_datetime_input) or validate_datetime_range_us(pickup_datetime_input)):
            await message.answer(f"⚠️ Error: Invalid Input\n\n"
                                 f"📅 The Pickup Date & Time must follow one of these formats:\n"
                                 f"🔹 Single Date & Time: 🕒 MM/DD/YYYY HH:MM\n"
                                 f"🔹 Time Range: 🕒 MM/DD/YYYY HH:MM - HH:MM\n\n"
                                 f"Examples:\n"
                                 f"-- Single: 01/01/2024 10:00\n"
                                 f"-- Range: 01/01/2024 09:00 - 17:00")
            return
        await state.update_data(pickup_datetime=pickup_datetime_input)

    elif datetime_type == "fcfs":
        # First Come First Serve: Automatically set value without validation
        await state.update_data(pickup_datetime="First Come First Serve")

    # Proceed to the next step after setting pickup_datetime
    await message.answer(f"📍 Please provide the Delivery Location:\n\n"
                         f"📌 Example: 123 Main St, City, State, ZIP Code\n\n"
                         f"Accurate details help ensure timely delivery.")
    await AssignLoad.delivery_location.set()

@dp.message_handler(state=AssignLoad.delivery_location)
async def enter_delivery_location(message: types.Message, state: FSMContext):
    delivery_location = message.text

    # Validate the delivery location format
    if not validate_location(delivery_location):
        await message.answer(
            f"⚠️ Error: Invalid Location Format\n\n"
            f"Please enter a valid delivery address with a ZIP code.\n\n"
            f"Example:\n"
            f"123 Main St, City, State, 12345"
        )
        return  # Stops here if the location is invalid, allowing the dispatcher to retry

    # If valid, store the location and proceed to the next step
    await state.update_data(delivery_location=delivery_location)
    await message.answer(f"🗓️ Select the Delivery Data & Time:\n\n"
                         f"-- Appointment Date & Time: Specify exact date and time.\n"
                         f"-- Date & Time (Range Possible): Provide a time range.\n"
                         f"-- First Come First Serve: No specific appointment required", reply_markup=delivery_datetime_options)
    await AssignLoad.delivery_datetime.set()

@dp.callback_query_handler(text="delivery_appointment_datetime", state=AssignLoad.delivery_datetime)
async def select_delivery_appointment_datetime(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"📅 Delivery Appointment Date & Time Required\n\n"
                                 f"Please enter the delivery appointment date and time in this format:\n"
                                 f"🕒 MM/DD/YYYY HH:MM\n"
                                 f"Example: 12/25/2024 14:30")
    await state.update_data(datetime_type="appointment")
    await AssignLoad.delivery_datetime.set()
    await call.answer()

@dp.callback_query_handler(text="delivery_datetime_range", state=AssignLoad.delivery_datetime)
async def select_delivery_datetime_range(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"📅 Input Required: Delivery Date & Time Range\n\n"
                                 f"Kindly provide the delivery date and time range using the format:\n\n"
                                 f"Format: MM/DD/YYYY HH:MM - HH:MM\n"
                                 f"Example: 12/25/2024 14:30 - 18:00")
    await state.update_data(datetime_type="range")
    await AssignLoad.delivery_datetime.set()
    await call.answer()

@dp.callback_query_handler(text="delivery_fcfs", state=AssignLoad.delivery_datetime)
async def select_delivery_fcfs(call: CallbackQuery, state: FSMContext):
    await state.update_data(datetime_type="fcfs", delivery_datetime="First Come First Serve")
    await call.message.edit_text(f"📏 Input Needed: Loaded Miles\n\n"
                                 f"Kindly provide the total loaded miles. Ensure the value is positive and numeric.\n"
                                 f"Example: 150.5")
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
            await message.answer(f"❌ Format Error\n\n"
                                 f"Please use the following format for entering the Delivery Date & Time:\n\n"
                                 f"MM/DD/YYYY HH:MM. Thank you!")
            return
        await state.update_data(delivery_datetime=delivery_datetime_input)

    elif datetime_type == "range":
        # Date & Time (Range Possible): Validate either single datetime or datetime range
        if not (validate_datetime_us(delivery_datetime_input) or validate_datetime_range_us(delivery_datetime_input)):
            await message.answer(f"📅 Date & Time Format Required\n\n"
                                 f"Your entry must follow one of the formats below:\n"
                                 f"-- Single Format: MM/DD/YYYY HH:MM\n"
                                 f"-- Range Format: MM/DD/YYYY HH:MM - HH:MM\n\n"
                                 f"Let’s fix this and proceed!")
            return
        await state.update_data(delivery_datetime=delivery_datetime_input)

    elif datetime_type == "fcfs":
        # First Come First Serve: Automatically set value without validation
        await state.update_data(delivery_datetime="First Come First Serve")

    # Proceed to the next step after setting delivery_datetime
    await message.answer(f"🚛 Loaded Miles Required\n\n"
                         f"Enter the loaded miles for this load.\n"
                         f"📝 Example: 123.45")
    await AssignLoad.loaded_miles.set()

@dp.message_handler(state=AssignLoad.loaded_miles)
async def enter_loaded_miles(message: types.Message, state: FSMContext):
    loaded_miles = message.text

    # Validate loaded miles using the regular expression
    if not validate_loaded_miles(loaded_miles):
        await message.answer(f"⚠️ Incorrect Format\n\n"
                             f"Loaded Miles must be a positive number.\n"
                             f"💡 Examples: 120 or 120.50. Please try again.")
        return

    # Convert to float for precision and update state
    await state.update_data(loaded_miles=float(loaded_miles))
    await message.answer(f"🛣️ Deadhead Miles Entry\n\n"
                         f"Please enter the Deadhead Miles as a positive number.\n"
                         f"📝 Example: 50 or 50.5.")
    await AssignLoad.deadhead_miles.set()

@dp.message_handler(state=AssignLoad.deadhead_miles)
async def enter_deadhead_miles(message: types.Message, state: FSMContext):
    deadhead_miles = message.text

    # Validate deadhead miles using the regular expression
    if not validate_loaded_miles(deadhead_miles):  # Reusing validate_loaded_miles for similar validation
        await message.answer(f"⚠️ Invalid Deadhead Miles\n\n"
                             f"The input must be a positive number.\n"
                             f"📋 Example formats: 45 or 45.75.")
        return

    # Convert to float for precision and update state
    await state.update_data(deadhead_miles=float(deadhead_miles))
    await message.answer(f"💵 Enter Trip Rate\n\n"
                         f"Please provide the Trip Rate in numerical format.")
    await AssignLoad.load_rate.set()

@dp.message_handler(state=AssignLoad.load_rate)
async def enter_load_rate(message: types.Message, state: FSMContext):
    load_rate = message.text

    # Validate load rate using the regular expression
    if not validate_loaded_miles(load_rate):  # Reusing validate_loaded_miles for similar validation
        await message.answer(f"❌ Incorrect Load Rate Format\n\n"
                             f"Ensure you input a positive number for the Load Rate (examples: 1500, 1500.75).\nPlease try again.")
        return

    # Convert to float for precision and update state
    await state.update_data(load_rate=float(load_rate))

    # Retrieve all entered data from state
    data = await state.get_data()

    # Format the summary of load details
    summary = (
        f"📋 Load Review:\n\n"
        f"🚛 Truck Number: {data.get('truck_number')}\n"
        f"🆔 Load Number: {data.get('load_number')}\n"
        f"👤 Driver Name: {data.get('driver_name')}\n"
        f"💼 Broker Name: {data.get('broker_name')}\n"
        f"🏢 Company Name: {data['company_name']}\n"
        f"👥 Group Name: {data['group_name']}\n"
        f"📍 Pickup Location: {data.get('pickup_location')}\n"
        f"📅 Pickup Date & Time: {data.get('pickup_datetime')}\n"
        f"📍 Delivery Location: {data.get('delivery_location')}\n"
        f"📅 Delivery Date & Time: {data.get('delivery_datetime')}\n"
        f"🛣️ Loaded Miles: {data.get('loaded_miles')}\n"
        f"🛤️ Deadhead Miles: {data.get('deadhead_miles')}\n"
        f"💵 Load Rate: {data.get('load_rate')}\n"
        f"👥 Load Type: {data.get('team_or_solo')}\n"
        f"📝 Dispatcher Name: {data['dispatcher_name']}\n"
    )

    await message.answer(summary + "\n\nPlease carefully review all the entered load details to ensure accuracy. Once confirmed, you can choose to submit the information or make edits if needed.\n"
                                   "🔍 Double-check everything to avoid errors before proceeding.", reply_markup=confirmation_options)
    await AssignLoad.confirmation.set()


@dp.callback_query_handler(text="confirm_send_data", state=AssignLoad.confirmation)
async def handle_send_data(call: types.CallbackQuery, state: FSMContext):
    try:
        # Retrieve load assignment data from FSMContext
        data = await state.get_data()

        formatted_rate = "${:,.2f}".format(data.get('load_rate', 0))  # Format rate with commas and two decimals
        load_assignment_message = (
            f"🚛 Assigned Load Information – Confirm all entries.\n\n"
            f"🔹 Load Number: {data.get('load_number')}\n"
            f"🔹 Broker: {data.get('broker_name')}\n"
            f"🔹 Type: {data.get('team_or_solo')}\n\n"
            
            f"📅 Pickup Details:\n"
            f"🕒 Date/Time - {data.get('pickup_datetime')}\n"
            f"📍 Location - {data.get('pickup_location')}.\n\n"
            
            f"📦 Delivery Details:\n"
            f"🕒 Date/Time - {data.get('delivery_datetime')}\n"
            f"📍 Location - {data.get('delivery_location')}.\n\n"
            
            f"📏 Total Miles: {data.get('loaded_miles')}\n"
            f"💵 Rate: {formatted_rate}\n\n"
            
            f"📜 Company's Policy – Payment is contingent on the submission of the BOL.\n"
            f"🏦 Payment Policy: No BOL, No Money.\n\n"
            
            f"❗ Avoid penalties by following guidelines: Key infractions detailed below.\n\n"
            
            f"- Late for pickup/delivery on street loads (without reason): $300\n"
            f"- Driver communication issues: $400\n"
            f"- No Amazon Relay app/TMS: $400\n"
            f"- Late for pickup/delivery on Amazon loads (without reason): $500\n"
            f"- No update provided: $400\n"
            f"- Rejecting confirmed load: $1000\n\n"
            
            f"🚨 Operational Notes: Critical steps to avoid delays.\n\n"
            f"- Always inform DISPATCHERS of traffic, construction, or weather delays.\n"
            f"- Scale the load after pickup to avoid axle overweight issues.\n"
            f"- Never leave the loaded trailer unattended.\n"
            f"- Verify BOL correctness and upload using CamScan.\n"
            f"- Send trailer photos to the group chat immediately.\n"
        )

        # Send message to the driver's group
        group_id = int(data['group_id'])
        await call.bot.send_message(chat_id=group_id, text=load_assignment_message)

        # Upload data to Google Sheets
        sheet_data = [
            data["load_number"],
            data["company_name"],
            data["dispatcher_name"],
            data["driver_name"],
            data["truck_number"],
            data["broker_name"],
            data["team_or_solo"],
            data["pickup_location"],
            data["pickup_datetime"],
            data["delivery_location"],
            data["delivery_datetime"],
            data["deadhead_miles"],
            data["loaded_miles"],
            data["load_rate"],
        ]
        # Append data to Google Sheets
        try:
            append_load_assignment_data(sheet_data)
            await call.message.answer(
                "✅ Load assignment data has been sent to the driver's group and saved to Google Sheets!")
        except Exception as e:
            await call.message.answer(f"⚠️ An error occurred while saving to Google Sheets: {e}")

        # Finish the FSM state
        if state:
            await state.finish()

    except KeyError as e:
        logging.error(f"KeyError: {e}. Missing data in FSM context.")
        await call.message.answer()

    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        await call.message.answer(f"🚨 Issue Detected: We couldn't complete the load assignment. Please get in touch with support.\n"
                                  "admin: @iamurod")

    finally:
        # Acknowledge callback
        await call.answer()


# ====== END: Assign Load Feature (Dispatcher) ======
# ====== END: Assign Load Feature (Dispatcher) ======
# ====== END: Assign Load Feature (Dispatcher) ======


@dp.callback_query_handler(text="🔍 Truck Status Check", state=DispatchState.dispatch_main)
async def handle_truck_status(call: types.CallbackQuery):

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

@dp.callback_query_handler(text="🔚 End and Close", state=DispatchState.dispatch_main)
async def handle_close(call: types.CallbackQuery):
    await call.message.delete()
    # Add further handling here
