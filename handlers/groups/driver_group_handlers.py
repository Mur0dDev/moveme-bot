from aiogram import types
from loader import dp
from filters import IsGroup
from data.config import ADMINS  # Ensure ADMINS has the admin IDs
from sheet.google_sheets_integration import get_user_full_name_by_telegram_id, check_group_verification
from keyboards.inline.group_inline_keyboards import get_verification_request_keyboard

@dp.message_handler(IsGroup(), commands=['start'], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def group_start_command(message: types.Message):
    user_id = message.from_user.id
    group_id = message.chat.id
    group_title = message.chat.title

    # Step 1: Check if the user is registered
    full_name = get_user_full_name_by_telegram_id(user_id)
    if full_name is None:
        await message.reply("You are not registered with the bot, so you do not have access to use it.")
        return

    # Step 2: Check if the group is verified
    if not check_group_verification(group_id):
        await message.reply(
            f"Hello, {full_name}! This group is not yet verified for bot usage. "
            "An approval request has been sent to the admin.", reply_markup=get_verification_request_keyboard()
        # # Notify admin about the request
        # for admin_id in ADMINS:
        #     await dp.bot.send_message(
        #         admin_id,
        #         (
        #             f"Group Verification Request\n\n"
        #             f"Requester: {full_name}\n"
        #             f"User ID: {user_id}\n"
        #             f"Group ID: {group_id}\n"
        #             f"Group Title: {group_title}\n\n"
        #             "Please approve or deny the request and specify the group type."
        #         ),
        #         reply_markup=get_verification_request_keyboard()
        #     )
        )
        return

    # If the group is verified, proceed with the welcome message
    await message.reply(f"Welcome, {full_name}! This group is verified, and you have access to use the bot.")


