from aiogram.dispatcher.filters.state import State, StatesGroup

class UserState(StatesGroup):
    stored_message_id = State()
