from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Create buttons
start_button = KeyboardButton("Start")
settings_button = KeyboardButton("Settings")
about_button = KeyboardButton("About")

# Create keyboard
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(start_button).add(settings_button).add(about_button)
