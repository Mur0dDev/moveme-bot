from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_verification_request_keyboard():
    """
    Returns an InlineKeyboardMarkup for requesting admin approval or closing the request.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Send for Approval", callback_data="request_admin_approval"),
        InlineKeyboardButton("Close", callback_data="close_request")
    )
    return keyboard
