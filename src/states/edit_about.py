from aiogram.fsm.state import State, StatesGroup

class EditAboutStates(StatesGroup):
    name = State()
    surname = State()
    grade = State()

edit_about_states_words = {
    "name": "имя",
    "surname": "фамилию",
    "grade": "класс"
}