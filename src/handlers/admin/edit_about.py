from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter

from aiogram.fsm.context import FSMContext
from states.edit_about import EditAboutStates, edit_about_states_words

from keyboards.inline import grade_keyboard
from configs.database import get_db, is_admin, is_root

router = Router()

@router.callback_query(F.data.startswith("edit_"))
async def cbq_edit_about(cbq: CallbackQuery, state: FSMContext):
    if not await is_admin(cbq.from_user.id):
        return cbq.message.delete()
    
    data = cbq.data.split("_")
    key, user_id = data[1], data[2]

    db = get_db()

    user_cur = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_rows = await user_cur.fetchone()

    if not user_rows: return

    await cbq.message.edit_text(
        f"✍️ Вы изменяете {edit_about_states_words[key]} пользователю {user_rows[2]} {user_rows[1]}. Укажите новое значение параметра",
        reply_markup=await grade_keyboard(is_admin=True) if key == "grade" else None
    )
    
    await state.set_state(getattr(EditAboutStates, key))
    await state.update_data(user_id=user_id, state=key)

@router.callback_query(F.data.startswith("grade_"), EditAboutStates.grade)
async def cbq_grade(cbq: CallbackQuery, state: FSMContext):
    if not await is_admin(cbq.from_user.id):
        await state.clear()
        return cbq.message.delete()
    
    grade_id = cbq.data.replace("grade_", "")
    data = await state.get_data()
    
    db = get_db()
    
    await db.execute("UPDATE users SET grade_id = ? WHERE id = ?", (grade_id, data["user_id"],))
    await db.commit()

    await cbq.answer("Успешно!")
    await cbq.message.delete()

    try:
        await cbq.bot.send_message(data["user_id"], "📚 Администратор изменил вам класс")
    except: pass

    await state.clear()

@router.message(StateFilter(EditAboutStates.name, EditAboutStates.surname))
async def msg_edit_name_or_surname(msg: Message, state: FSMContext):
    if not await is_admin(msg.from_user.id):
        await state.clear()
        return msg.delete()
    
    data = await state.get_data()
    
    if not msg.text or len(msg.text.split()) > 1:
        return await msg.reply(f"⚠️ {edit_about_states_words[data['state']].capitalize()} необходимо указать одним словом")
    
    db = get_db()
    
    await db.execute(f"UPDATE users SET {data['state']} = ? WHERE id = ?", (msg.text.capitalize(), data["user_id"],))
    await db.commit()

    await msg.reply("⚙️ Успешно!")

    try:
        await msg.bot.send_message(data["user_id"], f"✍️ Администратор изменил вам {edit_about_states_words[data['state']]}")
    except: pass

    await state.clear()

@router.callback_query(F.data.startswith("admin_"))
async def cbq_admin(cbq: CallbackQuery):
    if not await is_root(cbq.from_user.id):
        return cbq.message.delete()
    
    user_id = cbq.data.split("_")[1]
    
    db = get_db()

    await db.execute("UPDATE users SET is_admin = 1 - is_admin WHERE id = ?", (user_id,))
    await db.commit()

    await cbq.answer("Успешно!")
    await cbq.message.delete()

    try:
        await cbq.bot.send_message(user_id, f"👀 Ваши права администратора были изменены")
    except: pass