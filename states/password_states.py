from aiogram.dispatcher.filters.state import State, StatesGroup

class PasswordState(StatesGroup):
    """
    States for the password management workflow.
    """
    verify_user = State()         # Verify if the user has access to the password feature
    search_email = State()        # State for searching email
    select_email = State()        # State for selecting a specific email
    add_comment = State()         # State for asking the user for a comment before full access
