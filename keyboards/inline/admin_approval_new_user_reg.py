from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_approval_new_user = InlineKeyboardMarkup(
    inline_keyboard=[
    [
        InlineKeyboardButton(text="✅ Send for Approval", callback_data="✅ Send for Approval"),
    ],
    [
        InlineKeyboardButton(text="❌ Close", callback_data="❌ Close"),
    ]
])
