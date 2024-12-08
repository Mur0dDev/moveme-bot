import asyncio
import os
import re
import json

import boto3
import logging
from aiogram import types
from loader import dp
from data.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
from aiogram.dispatcher.filters import Text
from sheet.google_sheets_integration import get_full_name_by_user_id, search_truck_details
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified

# Initialize logging for error tracking
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Amazon Textract Client
textract_client = boto3.client(
    "textract",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)



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
    Process the photo with Amazon Textract and display structured JSON in PyCharm terminal.
    Notify the user about the result being displayed in the terminal.
    """
    loading_message = await message.reply("🔄 Starting photo processing...")

    try:
        # Simulate percentage progress
        for percent in range(0, 101, 20):
            await loading_message.edit_text(f"🔄 Processing your photo... {percent}% complete")
            await asyncio.sleep(0.5)

        # Retrieve and process the photo
        file_id = message.photo[-1].file_id
        file_info = await message.bot.get_file(file_id)
        downloaded_file = await message.bot.download_file(file_info.file_path)

        # Convert BytesIO to bytes
        file_bytes = downloaded_file.read()

        # Call Textract API
        response = textract_client.detect_document_text(Document={"Bytes": file_bytes})

        # Extract text lines
        extracted_lines = [item["Text"] for item in response["Blocks"] if item["BlockType"] == "LINE"]

        # Process text to structure the JSON
        structured_data = process_extracted_text(extracted_lines)

        # Display structured JSON in the terminal
        print("✅ Structured Load Data (JSON):")
        print(json.dumps(structured_data, indent=4))

        # Notify the user
        await message.answer("✅ Photo processed successfully!\n\nThe result has been displayed in the developer's console/terminal.")

    except Exception as e:
        logging.error("An error occurred while processing the photo", exc_info=True)
        await message.reply("❌ An error occurred while processing your photo. Please try again later.")

# Function to process extracted text into structured JSON
def process_extracted_text(extracted_lines):
    """
    Parse the extracted text lines and structure them into JSON format.
    """
    # Initialize the structured data
    structured_data = {
        "LoadID": None,
        "Distance": None,
        "RatePerMile": None,
        "TotalRate": None,
        "Pickup": {
            "Location": None,
            "Address": None,
            "Scheduled": None,
            "Actual": None,
            "TrailerID": None,
            "Status": None,
        },
        "Delivery": {
            "Location": None,
            "Address": None,
            "Scheduled": None,
            "Actual": None,
            "TrailerID": None,
        },
        "Driver": None,
        "Equipment": {
            "TractorID": None,
            "TrailerType": None,
        },
    }

    # Extract key fields
    try:
        # Load ID
        structured_data["LoadID"] = next((line for line in extracted_lines if re.match(r"^\d+[A-Z0-9]+$", line)), None)

        # Distance
        structured_data["Distance"] = next((line for line in extracted_lines if "mi" in line), None)

        # Rate Per Mile and Total Rate
        structured_data["RatePerMile"] = next((line for line in extracted_lines if "/mi" in line), None)
        structured_data["TotalRate"] = next((line for line in extracted_lines if line.startswith("$") and "/mi" not in line), None)

        # Driver
        structured_data["Driver"] = next((line for line in extracted_lines if re.match(r"^[A-Z]\.\s[A-Z][a-z]+$", line)), None)

        # Pickup Details
        pickup_start = extracted_lines.index("Pick-up instructions") - 5  # Offset to find pickup details
        structured_data["Pickup"]["Location"] = extracted_lines[pickup_start]
        structured_data["Pickup"]["Address"] = extracted_lines[pickup_start + 1]
        structured_data["Pickup"]["Scheduled"] = next((line for line in extracted_lines if "Sch" in line and "Pick-up" in line), None)
        structured_data["Pickup"]["Actual"] = next((line for line in extracted_lines if "CPT" in line and "Pick-up" in line), None)
        structured_data["Pickup"]["TrailerID"] = next((line for line in extracted_lines if "Trailer ID" in line), None)
        structured_data["Pickup"]["Status"] = next((line for line in extracted_lines if "Preloaded" in line), None)

        # Delivery Details
        delivery_start = extracted_lines.index("Drop-off instructions") - 5  # Offset to find delivery details
        structured_data["Delivery"]["Location"] = extracted_lines[delivery_start]
        structured_data["Delivery"]["Address"] = extracted_lines[delivery_start + 1]
        structured_data["Delivery"]["Scheduled"] = next((line for line in extracted_lines if "Sch" in line and "Drop-off" in line), None)
        structured_data["Delivery"]["Actual"] = next((line for line in extracted_lines if "CPT" in line and "Drop-off" in line), None)
        structured_data["Delivery"]["TrailerID"] = next((line for line in extracted_lines if "Trailer ID" in line and delivery_start in extracted_lines), None)

        # Equipment Details
        structured_data["Equipment"]["TractorID"] = next((line for line in extracted_lines if "Tractor ID" in line), None)
        structured_data["Equipment"]["TrailerType"] = next((line for line in extracted_lines if "53" in line and "Trailer" in line), None)

    except Exception as e:
        logging.error("Error while parsing extracted text", exc_info=True)

    return structured_data



@dp.message_handler(content_types=types.ContentType.ANY, state="*")
async def handle_invalid_content(message: types.Message):
    """
    Handler to reject invalid content types (non-photo).
    """
    await message.reply("❌ Invalid file type. Please send a photo in .png format.")
