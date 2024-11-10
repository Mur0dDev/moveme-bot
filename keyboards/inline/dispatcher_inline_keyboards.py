from data.dispatcher_texts import get_random_message, assign_load_options, truck_status_options, close_options
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


dispatcher_main_features = InlineKeyboardMarkup(
    inline_keyboard=[
    [
        InlineKeyboardButton(text=get_random_message(assign_load_options), callback_data="🛠️ Load Assign"),
    ],
    [
        InlineKeyboardButton(text=get_random_message(truck_status_options), callback_data="🔍 Truck Status Check")
    ],
    [
        InlineKeyboardButton(text=get_random_message(close_options), callback_data="🔚 End and Close"),
    ]
])
