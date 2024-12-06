import asyncio
import os

import boto3
from aiogram import types
from loader import dp  # Adjust the import if your Dispatcher instance is elsewhere
from aiogram.dispatcher.filters import Text
from sheet.google_sheets_integration import get_full_name_by_user_id, search_truck_details
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified


# Initialize Amazon Textract Client
textract_client = boto3.client("textract", region_name="eu-west-1")  # Update your region as needed


@dp.message_handler(commands=['assignload'], state="*")
async def assign_load_handler(message: types.Message):
    """
    Handler for the /assignload command. Works in any state.
    """
    user_id = message.from_user.id

    # Get dispatcher full name
    dispatcher_name = get_full_name_by_user_id(user_id)
    if not dispatcher_name:
        await message.reply("❌ You are not registered in the system. Please contact an admin.")
        return

    # Respond with instructions to assign a load
    await message.reply(
        f"🛠️ Hello {dispatcher_name}!\n\n"
        "Ready to assign a new load. Please provide the Truck Number to proceed.\n\n"
        "🚛 Example: `/assignload TRUCK123`\n"
        "You can also share a truck number directly using this command."
    )


@dp.message_handler(state="*")
async def search_and_select_truck_number(message: types.Message, state: FSMContext):
    """
    Handler to search for a truck by number and display matched results.
    """
    truck_number = message.text.strip()

    # Search for trucks in the group cache
    matched_trucks = search_truck_details(truck_number)

    if not matched_trucks:
        await message.reply(
            f"❌ No Matches Found:\n\n"
            f"We couldn’t find any trucks matching '{truck_number}'.\n"
            f"Please double-check and try again."
        )
        return

    # Save matched trucks and original truck number in FSMContext
    await state.update_data(matched_trucks=matched_trucks, searched_truck_number=truck_number)

    # Prepare results message
    results_message = "🔎 Search Results:\nHere are the trucks matching your query:\n\n"
    for idx, truck in enumerate(matched_trucks, start=1):
        results_message += (
            f"🔢 Result {idx}:\n"
            f"🚛 Truck Number: {truck['Truck Number']}\n"
            f"🏢 Company Name: {truck['Company Name']}\n"
            f"👨‍✈️ Driver Name: {truck['Driver Name']}\n"
            f"👥 Group Name: {truck['Group Name']}\n\n"
        )

    # Generate inline buttons for truck selection
    truck_buttons = InlineKeyboardMarkup(row_width=3)
    for idx in range(1, len(matched_trucks) + 1):
        truck_buttons.insert(
            InlineKeyboardButton(
                text=str(idx),
                callback_data=f"select_truck:{idx}"
            )
        )

    # Add a cancel button
    truck_buttons.add(
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_selection")
    )

    # Send results to the user
    await message.reply(results_message, reply_markup=truck_buttons)



@dp.callback_query_handler(Text(startswith="select_truck:"), state="*")
async def handle_truck_selection(call: types.CallbackQuery, state: FSMContext):
    """
    Handles truck selection from the list of matched trucks in any state.
    """
    _, selected_index = call.data.split(":")
    selected_index = int(selected_index) - 1  # Convert to zero-based index

    # Retrieve matched trucks from FSMContext
    data = await state.get_data()
    matched_trucks = data.get("matched_trucks")

    if not matched_trucks or selected_index < 0 or selected_index >= len(matched_trucks):
        await call.answer(
            "🚫 Hmm, that doesn’t look like a valid choice. No worries, give it another shot!",
            show_alert=True
        )
        return

    selected_truck = matched_trucks[selected_index]

    # Update FSM state with selected truck details
    await state.update_data(
        truck_number=selected_truck['Truck Number'],
        company_name=selected_truck['Company Name'],
        driver_name=selected_truck['Driver Name'],
        group_name=selected_truck['Group Name'],
        group_id=selected_truck.get('Group ID')  # Ensure Group ID is included
    )

    await call.message.edit_text(
        f"🚛 Truck Selection Successful!\n\n"
        f"Here are the details of your selected truck:\n"
        f"🚛 Truck Number: {selected_truck['Truck Number']}\n"
        f"🏢 Company Name: {selected_truck['Company Name']}\n"
        f"👨‍✈️ Driver Name: {selected_truck['Driver Name']}\n\n"
        f"🎯 Great choice! Now, let’s move forward.\n"
        f"📋 Please provide the load number."
    )
    await call.answer()


@dp.callback_query_handler(Text(equals="cancel_selection"), state="*")
async def cancel_truck_selection(call: types.CallbackQuery, state: FSMContext):
    """
    Cancels truck selection and resets the state in any state.
    """
    await call.message.answer(
        f"🚫 Truck Selection Canceled!\n\n"
        f"No worries, you can start fresh now.\n"
        f"🔄 Simply type /start to begin again."
    )
    # await state.finish()  # Finish any state instead of resetting to a specific one
    await call.answer()



@dp.message_handler(content_types=types.ContentType.PHOTO, state="*")
async def handle_photo_with_textract(message: types.Message, state: FSMContext):
    """
    Handler to process a photo with Amazon Textract and return extracted text without saving to disk.
    """
    # Step 1: Inform the user and simulate a loading animation
    loading_message = await message.reply("🔄 Processing your photo, please wait...")

    try:
        # Update loading message with a simulated animation
        for i in range(3):  # Simulate a few "loading" updates
            await loading_message.edit_text(f"🔄 Processing your photo{'.' * (i + 1)}")
            await asyncio.sleep(1)

        # Step 2: Retrieve photo file
        file_id = message.photo[-1].file_id  # Get the highest resolution photo
        file_info = await message.bot.get_file(file_id)
        downloaded_file = await message.bot.download_file(file_info.file_path)

        # Step 3: Process the photo with Amazon Textract in memory
        response = textract_client.detect_document_text(Document={"Bytes": downloaded_file})

        # Step 4: Extract text from Textract response
        extracted_text = []
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":  # Extract lines of text
                extracted_text.append(item["Text"])

        # Combine all extracted text
        extracted_text_str = "\n".join(extracted_text)

        # Step 5: Send the extracted text back to the user
        if extracted_text:
            await loading_message.edit_text(
                f"✅ Text extraction successful! Here's the text from your photo:\n\n{extracted_text_str}"
            )
        else:
            await loading_message.edit_text("❌ No text could be extracted from the photo.")

    except Exception as e:
        await loading_message.edit_text(
            f"❌ An error occurred while processing the photo: {str(e)}"
        )


@dp.message_handler(content_types=types.ContentType.ANY, state="*")
async def handle_invalid_content(message: types.Message):
    """
    Handler to reject invalid content types (non-photo).
    """
    await message.reply("❌ Invalid file type. Please send a photo in .png format.")
