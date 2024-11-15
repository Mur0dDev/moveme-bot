from aiogram import types
from loader import dp
from sheet.google_sheets_integration import handle_update_command, user_cache, group_cache, update_cache, \
    get_user_full_name_by_telegram_id, check_group_verification
from filters import IsSuperAdmin, IsPrivate

@dp.message_handler(IsPrivate(), IsSuperAdmin(), commands=['update'])
async def update_cache_command(message: types.Message):
    """
    Handler for the /update command. This command updates the cache for user and group data from Google Sheets.
    Only the super admin can execute this command.
    """
    # Await the update command and get the result message
    result_message = await handle_update_command()

    # Prepare a detailed report of the updated data
    user_data_summary = "\n".join([f"Telegram ID: {telegram_id}, Full Name: {data}" for telegram_id, data in user_cache.items()])
    group_data_summary = "\n".join([f"Group ID: {group_id}, Data: {data}" for group_id, data in group_cache.items()])

    # Compile the response message with cache summary
    response = f"{result_message}\n\nUpdated User Data:\n{user_data_summary}\n\nUpdated Group Data:\n{group_data_summary}"

    # Send the detailed update message to the admin
    await message.reply(result_message)



# from aiogram import types
# from loader import dp
# from sheet.google_sheets_integration import handle_update_command
# from filters import IsSuperAdmin, IsPrivate
#
# @dp.message_handler(IsPrivate(), IsSuperAdmin(), commands=['update'])
# async def update_cache_command(message: types.Message):
#     """
#     Handler for the /update command. This command updates the cache for user and group data from Google Sheets.
#     Only the super admin can execute this command.
#     """
#     result_message = handle_update_command()
#     await message.reply(result_message)
