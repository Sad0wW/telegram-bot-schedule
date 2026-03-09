from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

user_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📨 Расписание"),
            KeyboardButton(text="🔆 О себе")
        ]
    ], resize_keyboard=True
)

admin_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📨 Расписание"),
            KeyboardButton(text="📚 Классы")
        ],
        [
            KeyboardButton(text="👥 Пользователи"),
            KeyboardButton(text="🔆 О себе")
        ]
    ], resize_keyboard=True
)