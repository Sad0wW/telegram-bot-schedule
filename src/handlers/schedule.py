from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile

from aiogram.fsm.context import FSMContext
from states.schedule import ScheduleStates

from handlers.admin.users import cbq_search_user, msg_search_user

from keyboards.inline import schedule_keyboard, grade_keyboard, users_keyboard, send_schedule_keyboard, close_keyboard
from configs.database import get_db, is_admin

from pathlib import Path
from datetime import datetime

router = Router()

days_week = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

@router.message(F.text == "📨 Расписание")
async def msg_schedule(msg: Message):
    dir = Path("./schedule/").iterdir()
    weekday = datetime.now().weekday()

    schedule: list[tuple[str, str]] = []

    for d in dir:
        if not d.is_file() or d.suffix != ".jpg" or d.stem not in days_week:
            continue

        if weekday < days_week.index(d.stem):
            [f.unlink(missing_ok=True) for f in Path("./schedule/").iterdir() if f.is_file()]
            schedule.clear()
            break

        schedule.append((datetime.fromtimestamp(d.stat().st_birthtime).strftime("%d.%m.%Y"), d.name))

    await msg.reply(
        f"📨 На данный момент есть расписание на {len(schedule)} из 7 дней", 
        reply_markup=await schedule_keyboard(schedule, is_admin=True if await is_admin(msg.from_user.id) else False)
    )

@router.callback_query(F.data.startswith(days_week))
async def cbq_days_week(cbq: CallbackQuery):
    image = Path("./schedule/") / cbq.data
    
    if not image.exists() or not image.is_file():
        return await cbq.message.edit_text(f"❌ Не удалось получить расписание. Повторите попытку", reply_markup=None)
    
    try:
        await cbq.message.answer_photo(FSInputFile(f"./schedule/{cbq.data}"))
        await cbq.message.delete()
    except:
        await cbq.message.edit_text(f"❌ Не удалось получить расписание. Повторите попытку", reply_markup=None)

@router.callback_query(F.data == "send_schedule")
async def cbq_send_schedule(cbq: CallbackQuery, state: FSMContext):
    if not await is_admin(cbq.from_user.id):
        return await cbq.message.delete()
    
    await cbq.message.edit_text("📨 Отправьте фотографию расписания", reply_markup=close_keyboard)
    await state.set_state(ScheduleStates.loading_schedule)

@router.message(F.photo, ScheduleStates.loading_schedule)
async def msg_photo(msg: Message, state: FSMContext):
    if not await is_admin(msg.from_user.id):
        return await state.clear()
    
    await state.update_data(photo=msg.photo[-1])
    await msg.reply("📨 Выберите кому хотите отправить расписание", reply_markup=send_schedule_keyboard)

@router.callback_query(F.data.startswith("send_schedule_"))
async def cbq_send_schedule_option(cbq: CallbackQuery, state: FSMContext):
    if not await is_admin(cbq.from_user.id):
        await state.clear()
        return await cbq.message.delete()
    
    option = cbq.data.split("_")[2]

    match option:
        case "all":
            await cbq.message.edit_text("🔃 Идет отправка расписания...")

            db = get_db()
            data = await state.get_data()

            users_cur = await db.execute("SELECT id FROM users")
            users_rows = await users_cur.fetchall()

            for (user_id,) in users_rows:
                if user_id == cbq.from_user.id: continue

                try: await cbq.bot.send_photo(user_id, data["photo"].file_id, caption="🏫 Новое расписание!")
                except: pass

            try:
                await cbq.bot.download(data["photo"], destination=f"./schedule/{days_week[datetime.now().weekday()]}.jpg")
                await cbq.message.answer("💾 Расписание успешно сохранено!")
            except:
                await cbq.message.answer("⚠️ Не удалось сохранить расписание")

            await state.clear()

            await cbq.message.edit_text("✅ Расписание успешно отправлено!")
            await cbq.answer("Успешно!")
        case "grade":
            await state.set_state(ScheduleStates.select_grade)
            await cbq.message.edit_text("📚 Выберите класс, которому хотите отправить расписание", reply_markup=await grade_keyboard(select_grade=True))
        case "user":
            await state.set_state(ScheduleStates.select_user)
            await cbq.message.edit_text("👤 Выберите пользователя, которому хотите отправить расписание", reply_markup=await users_keyboard(select_user=True))

@router.callback_query(F.data.startswith("select_grade_"), ScheduleStates.select_grade)
async def cbq_select_grade(cbq: CallbackQuery, state: FSMContext):
    if not await is_admin(cbq.from_user.id):
        await state.clear()
        return await cbq.message.delete()
    
    await cbq.message.edit_text("🔃 Идет отправка расписания...")
    
    db = get_db()
    data = await state.get_data()
    grade_id = cbq.data.split("_")[2]

    users_cur = await db.execute("SELECT id FROM users WHERE grade_id = ?", (grade_id,))
    users_rows = await users_cur.fetchall()

    for (user_id,) in users_rows:
        if user_id == cbq.from_user.id: continue

        try: await cbq.bot.send_photo(user_id, data["photo"].file_id, caption="📚 Новое расписание!")
        except: pass

    await state.clear()

    await cbq.message.edit_text("✅ Расписание успешно отправлено!")
    await cbq.answer("Успешно!")

@router.callback_query(F.data.startswith("select_user_"))
async def cbq_select_user(cbq: CallbackQuery, state: FSMContext):
    if not await is_admin(cbq.from_user.id):
        await state.clear()
        return await cbq.message.delete()
    
    await cbq.message.edit_text("🔃 Идет отправка расписания...")
    
    data = await state.get_data()
    user_id = int(cbq.data.split("_")[2])

    try: await cbq.bot.send_photo(user_id, data["photo"].file_id, caption="👤 Новое расписание!")
    except: pass

    await state.clear()

    await cbq.message.edit_text("✅ Расписание успешно отправлено!")
    await cbq.answer("Успешно!")

@router.callback_query(F.data.startswith("select_search_user"))
async def cbq_select_search_user(cbq: CallbackQuery, state: FSMContext):
    await cbq_search_user(cbq, state, True)

@router.message(ScheduleStates.search_user)
async def msg_select_search_user(msg: Message, state: FSMContext):
    await msg_search_user(msg, state, True)