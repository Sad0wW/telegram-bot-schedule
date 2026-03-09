from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext
from states.registration import RegistrationStates

from configs.database import is_registered, get_db

from keyboards.inline import grade_keyboard
from keyboards.reply import user_markup, admin_markup

router = Router()

@router.message(CommandStart(ignore_case=True))
async def cmd_start(msg: Message, state: FSMContext):
    if not await is_registered(msg.from_user.id):
        await msg.reply(f"👋 Добро пожаловать, {msg.from_user.full_name}! Я помогу автоматизировать процесс получения расписания для вашего класса")

        await msg.reply(
            "❗ Чтобы воспользоваться ботом, необходимо зарегистрироваться. Выберите свой класс из предоставленного списка", 
            reply_markup=await grade_keyboard()
        )

        return await state.set_state(RegistrationStates.grade)
    
    db = get_db()

    user_cur = await db.execute("SELECT * FROM users WHERE id = ?", (msg.from_user.id,))
    user_rows = await user_cur.fetchone()
    
    await msg.reply(
        f"{'👀' if user_rows[4] == 1 else '👋'} {user_rows[2]} {user_rows[1]}, здравствуйте! Выберите пункт из выпадающего списка",
        reply_markup=admin_markup if user_rows[4] == 1 else user_markup
    )

@router.callback_query(F.data.startswith("grade_"), RegistrationStates.grade)
async def cbq_grade(cbq: CallbackQuery, state: FSMContext):
    grade_id = int(cbq.data.replace("grade_", ""))

    await cbq.message.answer("✍️ Записал! Теперь введите свое имя")

    await state.update_data(grade_id=grade_id)
    await state.set_state(RegistrationStates.name)

@router.message(RegistrationStates.name)
async def msg_name(msg: Message, state: FSMContext):
    if not msg.text or len(msg.text.split()) > 1:
        return await msg.reply("⚠️ Имя должно быть указано одним словом")
    
    name = msg.text.capitalize()

    await msg.reply(f"🤝 Приятно познакомиться, {name}! Теперь введите свою фамилию")
    
    await state.update_data(name=name)
    await state.set_state(RegistrationStates.surname)

@router.message(RegistrationStates.surname)
async def msg_surname(msg: Message, state: FSMContext):
    if not msg.text or len(msg.text.split()) > 1:
        return await msg.reply("⚠️ Фамилия должна быть указано одним словом")
    
    surname = msg.text.capitalize()
    data = await state.get_data()
    
    await msg.reply(
        f"🚀 {surname} {data['name']}, регистрация завершена! Можете выбрать пункт из выпадающего списка",
        reply_markup=user_markup
    )

    db = get_db()

    await db.execute(
        "INSERT INTO users(id, grade_id, name, surname) VALUES(?, ?, ?, ?)",
        (msg.from_user.id, data["grade_id"], data["name"], surname,)
    )
    await db.commit()
    
    await state.clear()