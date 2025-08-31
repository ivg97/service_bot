from aiogram.fsm.state import State, StatesGroup

class BookingStates(StatesGroup):
    waiting_for_service = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_confirmation = State()

class AdminStates(StatesGroup):
    waiting_for_service_name = State()
    waiting_for_service_price = State()
    waiting_for_service_duration = State()