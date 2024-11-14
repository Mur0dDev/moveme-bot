from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

# Define the admin ID
ADMIN_ID = 5159723225

class IsSuperAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        # Check if the message is from the admin
        return message.from_user.id == ADMIN_ID
