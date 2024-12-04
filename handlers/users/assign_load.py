from aiogram import types
from loader import dp  # Adjust the import if your Dispatcher instance is elsewhere
from sheet.google_sheets_integration import get_full_name_by_user_id, search_truck_details


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
