from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_verification_request_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Approve", callback_data="approve_group"),
        InlineKeyboardButton("Deny", callback_data="deny_group")
    )
    return keyboard

def get_group_verification_keyboard():
    """
    Returns an InlineKeyboardMarkup with specified buttons:
    - GM Cargo LLC
    - Elmir INC
    - Close
    - Send to Pending
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("GM Cargo LLC", callback_data="verify_gm_cargo"),
        InlineKeyboardButton("Elmir INC", callback_data="verify_elmir"),
        InlineKeyboardButton("Close", callback_data="close_verification")
    )
    return keyboard
