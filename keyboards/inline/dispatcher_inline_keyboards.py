from data.dispatcher_texts import get_random_message, assign_load_options, truck_status_options, close_options
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Create dispatcher main features inline keyboard with randomly selected button texts
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

dispatcher_start_over = InlineKeyboardMarkup(
    inline_keyboard=[
    [
        InlineKeyboardButton(text="🔄 Start Over", callback_data="Start Over"),
    ],
])

team_or_solo_driver = InlineKeyboardMarkup(
    inline_keyboard=[
    [
        InlineKeyboardButton(text="👥 Team", callback_data="team"),
    ],
    [
        InlineKeyboardButton(text="👤 Solo", callback_data="solo"),
    ]
])


# Inline keyboard for Pickup Date & Time options
pickup_datetime_options = InlineKeyboardMarkup(row_width=1)
pickup_datetime_options.add(
    InlineKeyboardButton(text="📅 Appointment Date & Time", callback_data="appointment_datetime"),
    InlineKeyboardButton(text="⏰ Date & Time (Range Possible)", callback_data="datetime_range"),
    InlineKeyboardButton(text="🚛 First Come First Serve", callback_data="fcfs")
)

# Inline keyboard for Delivery Date & Time options
delivery_datetime_options = InlineKeyboardMarkup(row_width=1)
delivery_datetime_options.add(
    InlineKeyboardButton(text="📅 Appointment Date & Time", callback_data="delivery_appointment_datetime"),
    InlineKeyboardButton(text="⏰ Date & Time (Range Possible)", callback_data="delivery_datetime_range"),
    InlineKeyboardButton(text="🚛 First Come First Serve", callback_data="delivery_fcfs")
)


# Inline keyboard for confirmation options
confirmation_options = InlineKeyboardMarkup(row_width=1)
confirmation_options.add(
    InlineKeyboardButton(text="✅ Send Data", callback_data="confirm_send_data"),
    InlineKeyboardButton(text="✏️ Edit", callback_data="confirm_edit"),
    InlineKeyboardButton(text="❌ Close", callback_data="confirm_close")
)


