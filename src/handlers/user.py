from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext

from keyboards.inline import edit_about_user
from configs.database import get_db

router = Router()

@router.message(F.text == "🔆 О себе")
async def msg_about(msg: Message):
    db = get_db()

    user_cur = await db.execute("SELECT * FROM users WHERE id = ?", (msg.from_user.id,))
    user_rows = await user_cur.fetchone()

    if not user_rows: return

    grades_cur = await db.execute("SELECT name FROM grades WHERE id = ?", (user_rows[3],))
    grades_rows = await grades_cur.fetchone()

    if user_rows[4] == 1:
        await msg.reply(
            f"🔆 Информация о {user_rows[2]} {user_rows[1]}\n\n📚 Дожность: Администратор | {grades_rows[0]}",
            reply_markup=await edit_about_user(0, msg.from_user.id)
        )
    else:
        await msg.reply(f"🔆 Информация о {user_rows[2]} {user_rows[1]}\n\n📚 Обучается: {grades_rows[0]} класс")

@router.callback_query(F.data == "close")
async def cbq_close(cbq: CallbackQuery, state: FSMContext):
    await state.clear()
    await cbq.message.delete()