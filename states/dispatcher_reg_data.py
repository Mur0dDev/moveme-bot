from aiogram.dispatcher.filters.state import StatesGroup, State


class PersonalData(StatesGroup):
    realName = State()
    DOB = State()
    phoneNumber = State()