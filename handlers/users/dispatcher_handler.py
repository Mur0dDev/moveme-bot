# Imports
from aiogram import types
from loader import dp
from filters import IsPrivate
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher import FSMContext
from states.dispatcher_reg_data import DispatchState
from sheet.google_sheets_integration import get_full_name_by_user_id
from data.dispatcher_texts import get_random_greeting
from keyboards.inline.dispatcher_inline_keyboards import dispatcher_main_features


@dp.message_handler(IsPrivate(), CommandStart(), state=DispatchState.dispatch_main)
async def dispatcher_main(message: types.Message):
    """Main menu for dispatcher-specific features."""
    # Get the user's Telegram ID
    user_id = message.from_user.id

    # Retrieve the full name from Google Sheets based on user_id
    full_name = get_full_name_by_user_id(user_id)

    await message.answer(get_random_greeting(full_name), reply_markup=dispatcher_main_features)



