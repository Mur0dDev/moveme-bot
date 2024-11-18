from aiogram.dispatcher.filters.state import State, StatesGroup


class GroupVerificationStates(StatesGroup):
    """
    States related to group verification by super admins.
    """
    group_type = State()  # Selecting the type of group (e.g., drivers, management)
    company_name = State()  # Selecting the company name (e.g., GM Cargo LLC, Elmir INC)
    truck_number = State()  # Entering the truck number for drivers' group
    driver_name = State()  # Entering the driver name for drivers' group


class CacheManagementStates(StatesGroup):
    """
    States related to cache management by super admins.
    """
    updating_cache = State()  # Super admin triggers the cache update
