from aiogram.dispatcher.filters.state import State, StatesGroup

class AssignLoad(StatesGroup):
    company_name = State()
    driver_name = State()
    truck_number = State()
    load_number = State()
    broker_name = State()
    team_or_solo = State()
    pickup_location = State()
    pickup_datetime = State()
    delivery_location = State()
    delivery_datetime = State()
    loaded_miles = State()
    deadhead_miles = State()
    load_rate = State()
    confirmation = State()
