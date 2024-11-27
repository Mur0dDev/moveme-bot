from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from keyboards.default.main_menu import main_menu
from states.user_state import UserState

@dp.message_handler(commands=["start"])
async def handle_start(message: types.Message, state: FSMContext):
    await message.delete()
    # Send the initial message with the keyboard
    sent_message = await message.answer(
        "Welcome to the MoveMeGroup Bot! Choose an option:",
        reply_markup=main_menu
    )
    print(sent_message.message_id)
    # Set the state and store the message_id
    await UserState.stored_message_id.set()
    await state.update_data(
        stored_message_id=sent_message.message_id,
        chat_id=message.chat.id
    )

    # Debug: Log the chat_id and message_id
    print(f"Stored chat_id: {message.chat.id}, message_id: {sent_message.message_id}")

@dp.message_handler(lambda message: message.text == "Start", state=UserState.stored_message_id)
async def handle_start_button(message: types.Message, state: FSMContext):
    await message.delete()
    # Retrieve stored message_id and chat_id
    data = await state.get_data()
    message_id = data.get("stored_message_id")
    chat_id = data.get("chat_id")

    if message_id and chat_id:
        try:
            # Delete the old message
            await message.bot.delete_message(chat_id=chat_id, message_id=message_id)

            # Send a new message
            new_message = await message.answer(
                "You clicked 'Start'. The keyboard is now hidden.",
                reply_markup=types.ReplyKeyboardRemove()
            )

            # Update the state with the new message_id
            await state.update_data(stored_message_id=new_message.message_id)
        except Exception as e:
            print(f"Error while deleting/sending message: {e}")
            await message.answer("An error occurred. Please try again.")
    else:
        await message.answer("No editable message found. Please restart with /start.")

    # Finish the state
    await state.finish()

@dp.message_handler(lambda message: message.text == "Settings", state=UserState.stored_message_id)
async def handle_settings_button(message: types.Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    message_id = data.get("stored_message_id")
    chat_id = data.get("chat_id")

    if message_id and chat_id:
        try:
            await message.bot.delete_message(chat_id=chat_id, message_id=message_id)
            new_message = await message.answer(
                "You clicked 'Settings'. The keyboard is now hidden.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.update_data(stored_message_id=new_message.message_id)
        except Exception as e:
            print(f"Error while deleting/sending message: {e}")
            await message.answer("An error occurred. Please try again.")
    else:
        await message.answer("No editable message found. Please restart with /start.")

    await state.finish()

@dp.message_handler(lambda message: message.text == "About", state=UserState.stored_message_id)
async def handle_about_button(message: types.Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    message_id = data.get("stored_message_id")
    chat_id = data.get("chat_id")

    if message_id and chat_id:
        try:
            await message.bot.delete_message(chat_id=chat_id, message_id=message_id)
            new_message = await message.answer(
                "You clicked 'About'. The keyboard is now hidden.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.update_data(stored_message_id=new_message.message_id)
        except Exception as e:
            print(f"Error while deleting/sending message: {e}")
            await message.answer("An error occurred. Please try again.")
    else:
        await message.answer("No editable message found. Please restart with /start.")

    await state.finish()
