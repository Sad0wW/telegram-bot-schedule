from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    name = State()
    surname = State()
    grade = State()