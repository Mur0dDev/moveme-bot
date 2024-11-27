from aiogram.dispatcher.filters.state import StatesGroup, State

# Define a StatesGroup for tracking the registration process.
class PersonalData(StatesGroup):
    """State definitions for the user registration process."""

    # The following states represent the steps in the registration workflow:
    realName = State()    # State for collecting the user's full name.
    DOB = State()         # State for collecting the user's date of birth.
    phoneNumber = State() # State for collecting the user's phone number.

class UnverifiedState(StatesGroup):
    unverified = State()

# New department-specific states
class DispatchState(StatesGroup):
    """States for users in the Dispatch department."""
    dispatch_main = State()

class SafetyState(StatesGroup):
    """States for users in the Safety department."""
    safety_main = State()

class DriverState(StatesGroup):
    """States for users in the Driver department."""
    driver_main = State()

class AccountingState(StatesGroup):
    """States for users in the Accounting department."""
    accounting_main = State()

# New Denied state for users who were denied
class DeniedState(StatesGroup):
    denied_main = State()