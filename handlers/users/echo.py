from aiogram import types
from filters import IsPrivate
from states.dispatcher_reg_data import PersonalData, DispatchState, SafetyState, DriverState, AccountingState, DeniedState
from data.texts import get_random_message, denial_messages

from loader import dp

@dp.message_handler(IsPrivate(), state=DeniedState.denied_main)
async def bot_echo(message: types.Message):
    await message.answer(get_random_message(denial_messages))

# Echo bot
@dp.message_handler(IsPrivate(), state=None)
async def bot_echo(message: types.Message):
    await message.answer(message.text)
