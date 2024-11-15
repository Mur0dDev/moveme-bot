from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_verification_request_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Approve", callback_data="approve_group"),
        InlineKeyboardButton("Deny", callback_data="deny_group")
    )
    return keyboard

