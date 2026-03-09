from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from states.grades import GradesStates

from keyboards.inline import grade_keyboard, delete_grade
from configs.database import get_db, is_admin

router = Router()

@router.message(F.text == "📚 Классы")
async def msg_grades(msg: Message):
    if not await is_admin(msg.from_user.id): return
    
    await msg.reply("📚 Выберите класс для редактирования", reply_markup=await grade_keyboard(edit_grades=True))

@router.callback_query(F.data.startswith("update_grade_"))
async def cbq_update_grade(cbq: CallbackQuery):
    if not await is_admin(cbq.from_user.id):
        return await cbq.message.delete()
    
    grade_id = cbq.data.split("_")[2]
    
    await cbq.message.edit_text(f"📚 Вы действительно хотите удалить класс #ID{grade_id}?", reply_markup=delete_grade(grade_id))

@router.callback_query(F.data.startswith("delete_grade_"))
async def cbq_delete_grade(cbq: CallbackQuery):
    if not await is_admin(cbq.from_user.id):
        return await cbq.message.delete()
    
    grade_id = cbq.data.split("_")[2]
    db = get_db()

    await db.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
    await db.commit()

    await grade_keyboard(reset_keyboard=True)

    await cbq.answer("Успешно!")
    await cbq.message.delete()

@router.callback_query(F.data == "create_grade")
async def cbq_create_grade(cbq: CallbackQuery, state: FSMContext):
    if not await is_admin(cbq.from_user.id):
        return await cbq.message.delete()
    
    await cbq.message.edit_text("📚 Введите название класса (максимум 3 символа)", reply_markup=None)

    await state.set_state(GradesStates.create)

@router.message(GradesStates.create)
async def msg_create_grade(msg: Message, state: FSMContext):
    if not await is_admin(msg.from_user.id):
        await state.clear()
        return await msg.delete()
    
    if not msg.text or len(msg.text) > 3:
        return await msg.reply("⚠️ Название класса может состоять максимум из 3 символов")
    
    db = get_db()

    try:
        await db.execute("INSERT INTO grades(name) VALUES(?)", (msg.text.upper(),))
        await db.commit()

        await msg.reply("⚙️ Успешно!")

        await grade_keyboard(reset_keyboard=True)
    except:
        await msg.reply("❌ Не удалось создать класс. Вероятнее всего, класс с таким именем уже существует")

    await state.clear()