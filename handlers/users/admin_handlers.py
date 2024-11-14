from aiogram import types
from loader import dp
from sheet.google_sheets_integration import handle_update_command
from filters import IsSuperAdmin, IsPrivate

@dp.message_handler(IsPrivate(), IsSuperAdmin(), commands=['update'])
async def update_cache_command(message: types.Message):
    """
    Handler for the /update command. This command updates the cache for user and group data from Google Sheets.
    Only the super admin can execute this command.
    """
    result_message = handle_update_command()
    await message.reply(result_message)
