from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

new_user_letsgo = InlineKeyboardMarkup(
    inline_keyboard=[
    [
        InlineKeyboardButton(text="Let's go! 🚀", callback_data="Let's go! 🚀"),
    ],
    [
        InlineKeyboardButton(text="❌ Close", callback_data="❌ Close"),
    ]
])


pickup_department = InlineKeyboardMarkup(
    inline_keyboard=[
    [
        InlineKeyboardButton(text="📋 Dispatch", callback_data="Dispatch – 📋"),
        InlineKeyboardButton(text="🛡️ Safety", callback_data="Safety – 🛡️")
    ],
    [
        InlineKeyboardButton(text="🚛 Driver", callback_data="Driver – 🚛"),
        InlineKeyboardButton(text="💰 Accounting", callback_data="Accountant – 💰️")
    ],
    [
        InlineKeyboardButton(text="⬅️ Back", callback_data="⬅️ Back"),
    ]
])