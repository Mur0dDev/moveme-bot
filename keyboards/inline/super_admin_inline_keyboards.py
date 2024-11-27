from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_verification_request_keyboard(group_id: int):
    """
    Returns an InlineKeyboardMarkup with Approve and Deny buttons, embedding the group ID in the callback data.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Approve", callback_data=f"approve_group:{group_id}"),
        InlineKeyboardButton("Deny", callback_data=f"deny_group:{group_id}")
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

def get_group_type_selection_keyboard(group_id: int):
    """
    Returns an InlineKeyboardMarkup for selecting the group type.
    :param group_id: The ID of the group to be associated with the selected type.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Drivers' Group", callback_data=f"set_group_type:drivers:{group_id}"),
        InlineKeyboardButton("Management Group", callback_data=f"set_group_type:management:{group_id}")
    )
    return keyboard
