from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import get_db_session, Service, User, Appointment
from keyboards import admin_keyboard
from states import AdminStates

router = Router()


@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message):
    session = get_db_session()

    total_users = session.query(User).count()
    total_appointments = session.query(Appointment).count()

    from datetime import datetime
    today_appointments = session.query(Appointment).filter(
        Appointment.appointment_time >= datetime.now().date()
    ).count()

    stats_text = (
        f"📊 Статистика:\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"📋 Всего записей: {total_appointments}\n"
        f"📅 Записей на сегодня: {today_appointments}"
    )

    session.close()
    await message.answer(stats_text)


@router.message(F.text == "➕ Добавить услугу")
async def add_service_start(message: Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_service_name)
    await message.answer("Введите название новой услуги:", reply_markup=None)


@router.message(AdminStates.waiting_for_service_name)
async def add_service_name(message: Message, state: FSMContext):
    await state.update_data(service_name=message.text)
    await state.set_state(AdminStates.waiting_for_service_price)
    await message.answer("Введите цену услуги:")


@router.message(AdminStates.waiting_for_service_price)
async def add_service_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        data = await state.get_data()

        session = get_db_session()
        service = Service(
            name=data['service_name'],
            price=price
        )

        session.add(service)
        session.commit()
        session.close()

        await message.answer(
            "✅ Услуга успешно добавлена!",
            reply_markup=admin_keyboard()
        )
        await state.clear()

    except ValueError:
        await message.answer("❌ Введите корректную цену (число)")