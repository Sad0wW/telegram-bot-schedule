from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext

from states.users import UsersStates
from states.schedule import ScheduleStates

from keyboards.inline import users_keyboard, search_user_keyboard, edit_about_user
from configs.database import get_db, is_admin

router = Router()

@router.message(F.text == "👥 Пользователи")
async def msg_users(msg: Message):
    if not await is_admin(msg.from_user.id): return

    await msg.reply(
        "👥 Выберите пользователя для редактирования данных", 
        reply_markup=await users_keyboard()
    )

@router.callback_query(F.data.startswith("swipe_users_"))
async def cbq_swipe_users(cbq: CallbackQuery):
    if not await is_admin(cbq.from_user.id):
        return await cbq.message.delete()
    
    last_id = int(cbq.data.split("_")[2])
    
    await cbq.message.edit_reply_markup(reply_markup=await users_keyboard(last_id))

@router.callback_query(F.data == "search_user")
async def cbq_search_user(cbq: CallbackQuery, state: FSMContext, select_user: bool = False):
    if not await is_admin(cbq.from_user.id):
        return await cbq.message.delete()
    
    await cbq.message.edit_text("🔎 Введите имя или фамилию пользователя", reply_markup=None)

    await state.set_state(UsersStates.search if not select_user else ScheduleStates.search_user)

@router.message(UsersStates.search)
async def msg_search_user(msg: Message, state: FSMContext, select_user: bool = False):
    if not await is_admin(msg.from_user.id):
        await state.clear()
        return await msg.delete()

    if not msg.text or len(msg.text.split()) > 2:
        return await msg.reply("⚠️ Значение не может содержать более 2 слов")
    
    data = msg.text.split()
    name, surname = data[0].capitalize(), data[-1].capitalize()
    
    keyboard = await search_user_keyboard(name, surname, select_user=select_user)
    keyboard_len = len(keyboard.inline_keyboard)

    if keyboard_len > 0:
        await msg.reply(f"🔎 Всего найдено {keyboard_len} пользователей", reply_markup=keyboard)
        
        if select_user:
            return await state.set_state(ScheduleStates.select_user)
    else:
        await msg.reply(f"🔎 К сожалению, пользователь «{msg.text}» не найден")

    await state.clear()

@router.callback_query(F.data.startswith("user_"))
async def cbq_edit_about_user(cbq: CallbackQuery):
    if not await is_admin(cbq.from_user.id):
        return await cbq.message.delete()
    
    user_id = int(cbq.data.split("_")[1])
    
    db = get_db()

    user_cur = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_rows = await user_cur.fetchone()

    if not user_rows: return

    grades_cur = await db.execute("SELECT name FROM grades WHERE id = ?", (user_rows[3],))
    grades_rows = await grades_cur.fetchone()

    await cbq.message.edit_text(
        f"🔆 Информация о {user_rows[2]} {user_rows[1]}\n\n📚 Дожность: {f'Администратор | {grades_rows[0]}' if user_rows[4] == 1 else grades_rows[0]}",
        reply_markup=await edit_about_user(cbq.from_user.id if user_id != cbq.from_user.id else 0, user_id)
    )