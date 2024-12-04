from aiogram import types
from loader import dp  # Adjust the import if your Dispatcher instance is elsewhere
from sheet.google_sheets_integration import get_full_name_by_user_id, search_truck_details
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext


@dp.message_handler(commands=['assignload'], state="*")
async def assign_load_handler(message: types.Message):
    """
    Handler for the /assignload command. Works in any state.
    """
    user_id = message.from_user.id

    # Get dispatcher full name
    dispatcher_name = get_full_name_by_user_id(user_id)
    if not dispatcher_name:
        await message.reply("❌ You are not registered in the system. Please contact an admin.")
        return

    # Respond with instructions to assign a load
    await message.reply(
        f"🛠️ Hello {dispatcher_name}!\n\n"
        "Ready to assign a new load. Please provide the Truck Number to proceed.\n\n"
        "🚛 Example: `/assignload TRUCK123`\n"
        "You can also share a truck number directly using this command."
    )


@dp.message_handler(state="*")
async def search_and_select_truck_number(message: types.Message, state: FSMContext):
    """
    Handler to search for a truck by number and display matched results.
    """
    truck_number = message.text.strip()

    # Search for trucks in the group cache
    matched_trucks = search_truck_details(truck_number)

    if not matched_trucks:
        await message.reply(
            f"❌ No Matches Found:\n\n"
            f"We couldn’t find any trucks matching '{truck_number}'.\n"
            f"Please double-check and try again."
        )
        return

    # Save matched trucks and original truck number in FSMContext
    await state.update_data(matched_trucks=matched_trucks, searched_truck_number=truck_number)

    # Prepare results message
    results_message = "🔎 Search Results:\nHere are the trucks matching your query:\n\n"
    for idx, truck in enumerate(matched_trucks, start=1):
        results_message += (
            f"🔢 Result {idx}:\n"
            f"🚛 Truck Number: {truck['Truck Number']}\n"
            f"🏢 Company Name: {truck['Company Name']}\n"
            f"👨‍✈️ Driver Name: {truck['Driver Name']}\n"
            f"👥 Group Name: {truck['Group Name']}\n\n"
        )

    # Generate inline buttons for truck selection
    truck_buttons = InlineKeyboardMarkup(row_width=3)
    for idx in range(1, len(matched_trucks) + 1):
        truck_buttons.insert(
            InlineKeyboardButton(
                text=str(idx),
                callback_data=f"select_truck:{idx}"
            )
        )

    # Add a cancel button
    truck_buttons.add(
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_selection")
    )

    # Send results to the user
    await message.reply(results_message, reply_markup=truck_buttons)
