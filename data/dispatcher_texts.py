# data/dispatcher_texts.py
import random

# Function to select a random message from a list
def get_random_message(options):
    """Returns a random message from the provided list of options."""
    return random.choice(options)

# List of greeting messages with placeholders for full_name
greeting_messages = [
    "Hello {full_name}! 👋 Glad to have you back! 🌟\n\nSo far, you have two options:\n🔹 1. Assign Load\n🔹 2. Truck Status\n\nHow can I assist you today? Just pick an option below! 😊",
    "Hey there, {full_name}! 🙌 Ready to support you again!\n\nHere’s what you can do:\n🚚 1️⃣ Assign Load\n📊 2️⃣ Truck Status\n\nLet me know which one you'd like to work on. Just tap a choice below! 👇",
    "Welcome back, {full_name}! 🎉 Happy to assist you!\n\nCurrently, you have two options:\n1️⃣ Assign Load\n2️⃣ Truck Status\n\nPlease choose what you'd like help with today! 🛠️",
    "Hey {full_name}! 👋 Great to see you again!\n\nHere’s what I can help with:\n🚛 1. Assign Load\n📝 2. Truck Status\n\nJust pick one, and I’ll be right here to help you get started! 👍",
    "Hi {full_name}! 😊 Welcome back!\n\nYour available options are:\n🔸 1️⃣ Assign Load\n🔸 2️⃣ Truck Status\n\nLet me know how I can assist. Just select one of the options below! 👇"
]

# Function to get a random greeting message
def get_random_greeting(full_name):
    # Choose a random message from the list and format it with full_name
    return random.choice(greeting_messages).format(full_name=full_name)

assign_load_options = [
    "🚚 Assign Load",
    "📦 Load Assignment",
    "📝 Set Up a Load",
    "🚛 Dispatch a Load",
    "🛠️ Load Assign"
]

truck_status_options = [
    "🚛 Truck Status",
    "📊 Check Truck Status",
    "🛣️ Truck Current Status",
    "📍 View Truck Status",
    "🔍 Truck Status Check"
]

close_options = [
    "❌ Close",
    "✖️ Close Window",
    "🛑 Stop and Close",
    "🔚 End and Close"
]

truck_status_under_development_messages = [
    "🚧 Truck Status feature is still in the works! We’ll keep you updated once it’s ready. Thank you for your patience!",
    "🛠️ The Truck Status feature is currently under development. We’ll let you know as soon as it’s available. Thanks for your understanding!",
    "🔍 We're working hard to bring you the Truck Status feature! We'll notify you when it's good to go. Appreciate your patience!",
    "🚛 The Truck Status feature isn’t ready just yet. Stay tuned – we’ll update you once it’s launched. Thank you!"
]
