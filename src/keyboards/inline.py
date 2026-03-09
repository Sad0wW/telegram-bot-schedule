from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from configs.database import get_db, is_root

grade_markup = InlineKeyboardMarkup(inline_keyboard=[])

send_schedule_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=f"👤 Отправить пользователю", callback_data="send_schedule_user")],
    [InlineKeyboardButton(text=f"📚 Отправить классу", callback_data="send_schedule_grade")],
    [InlineKeyboardButton(text=f"🏫 Отправить всем", callback_data="send_schedule_all")]
])

close_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❎ Закрыть", callback_data="close")]
])

async def grade_keyboard(reset_keyboard: bool = False, is_admin: bool = False, edit_grades: bool = False, select_grade: bool = False) -> InlineKeyboardMarkup:
    if not reset_keyboard and not edit_grades and not select_grade and len(grade_markup.inline_keyboard) > 0: return grade_markup

    grade_markup.inline_keyboard.clear()

    db = get_db()

    grade_cur = await db.execute("SELECT * FROM grades")
    grade_rows = await grade_cur.fetchall()

    row: list[InlineKeyboardButton] = []
    for grade_id, grade_name in grade_rows:
        if not is_admin and grade_name == "-": continue

        callback_data = f"grade_{grade_id}"

        if edit_grades:
            callback_data = "update_" + callback_data
        elif select_grade:
            callback_data = "select_" + callback_data

        row.append(InlineKeyboardButton(text=grade_name, callback_data=callback_data))

        if len(row) == 3:
            grade_markup.inline_keyboard.append(row)
            row = []

    if row:
        grade_markup.inline_keyboard.append(row)

    keyboard = InlineKeyboardMarkup(inline_keyboard=grade_markup.inline_keyboard)

    if edit_grades:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="➕ Создать класс", callback_data="create_grade")
        ])

    if edit_grades or select_grade:    
        grade_markup.inline_keyboard.clear()

    return keyboard

def delete_grade(grade_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❗ ПОДТВЕРДИТЬ", callback_data=f"delete_grade_{grade_id}"),
            InlineKeyboardButton(text="❌ ОТМЕНИТЬ", callback_data="close")
        ]
    ])

async def edit_about_user(admin_id: int, user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👉 Изменить имя", callback_data=f"edit_name_{user_id}")],
        [InlineKeyboardButton(text="👈 Изменить фамилию", callback_data=f"edit_surname_{user_id}")],
        [InlineKeyboardButton(text="📚 Изменить класс", callback_data=f"edit_grade_{user_id}")]
    ])

    if await is_root(admin_id):
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="👀 Права администратора", callback_data=f"admin_{user_id}")])

    return keyboard

async def users_keyboard(last_id: int = 1, select_user: bool = False) -> InlineKeyboardMarkup:
    db = get_db()

    users_cur = await db.execute("SELECT * FROM users WHERE rowid >= ? ORDER BY rowid LIMIT 10", (last_id,))
    users_row = await users_cur.fetchall()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    row: list[InlineKeyboardButton] = []
    for user_id, name, surname, grade_id, is_admin in users_row:
        row.append(InlineKeyboardButton(text=f"{'👀 ' if is_admin == 1 else ''}{surname} {name}", callback_data=f"{'select_' if select_user else ''}user_{user_id}"))

        if len(row) == 3:
            keyboard.inline_keyboard.append(row)
            row = []

    if row:
        keyboard.inline_keyboard.append(row)

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="❎", callback_data="close"),
        InlineKeyboardButton(text="🔎", callback_data=f"{'select_' if select_user else ''}search_user"),
        InlineKeyboardButton(text="❎", callback_data="close")
    ])

    if last_id > 10:
        keyboard.inline_keyboard[0][0] = InlineKeyboardButton(text="⬅️", callback_data=f"swipe_users_{last_id - 10}")
        keyboard.inline_keyboard[0][-1] = InlineKeyboardButton(text="➡️", callback_data=f"swipe_users_{last_id + 10}")

    return keyboard

async def search_user_keyboard(name: str, surname: str, select_user: bool = False) -> InlineKeyboardMarkup:
    db = get_db()

    users_cur = await db.execute(
        "SELECT * FROM users WHERE name IN (?, ?) OR surname IN (?, ?)",
        (name, surname, name, surname)
    )
    users_row = await users_cur.fetchall()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    row: list[InlineKeyboardButton] = []
    for user_id, name, surname, grade_id, is_admin in users_row:
        row.append(InlineKeyboardButton(text=f"{'👀 ' if is_admin == 1 else ''}{surname} {name}", callback_data=f"{'select_' if select_user else ''}user_{user_id}"))

        if len(row) == 3:
            keyboard.inline_keyboard.append(row)
            row = []

    if row:
        keyboard.inline_keyboard.append(row)

    return keyboard

async def schedule_keyboard(schedule: list[tuple[str, str]], is_admin: bool = False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📅 {date}", callback_data=weekday)] for (date, weekday) in schedule
    ])

    if is_admin:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="📤 Отправить расписание", callback_data="send_schedule")])

    return keyboard