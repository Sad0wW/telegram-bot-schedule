from aiogram.fsm.state import State, StatesGroup

class ScheduleStates(StatesGroup):
    loading_schedule = State()
    select_grade = State()
    select_user = State()
    search_user = State()