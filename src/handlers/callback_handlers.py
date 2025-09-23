from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database import get_db_session, User, Service, Appointment
from keyboards import services_keyboard, date_keyboard, time_keyboard, \
    confirm_keyboard, main_menu_keyboard, \
    back_to_main_keyboard, delete_services_keyboard
from states import BookingStates
import config

router = Router()


@router.callback_query(F.data.startswith("service_"))
async def service_selected(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split('_')[1])
    session = get_db_session()
    service = session.query(Service).get(service_id)
    session.close()

    await state.update_data(service_id=service_id)
    await state.set_state(BookingStates.waiting_for_date)

    await callback.message.edit_text(
        f"📅 Вы выбрали: {service.name}\n💵 Цена: {service.price}₽\n⏱ Длительность: {service.duration} мин.\n\nВыберите дату:",
        reply_markup=date_keyboard()
    )

@router.callback_query(F.data.startswith("selectService_"))
async def service_selected(callback: CallbackQuery, state: FSMContext):
    app_id = int(callback.data.split('_')[1])
    with get_db_session() as session:
        app = session.query(Appointment).get(app_id)

        await callback.message.edit_text(
            f"📅 Ваша запись: {app.service.name}\n💵 Цена: {app.service.price}₽\n⏱ Длительность: {app.service.duration} мин.",
            reply_markup=delete_services_keyboard()
        )


@router.callback_query(F.data.startswith("date_"))
async def date_selected(callback: CallbackQuery, state: FSMContext):
    selected_date = callback.data.split('_')[1]
    data = await state.get_data()

    session = get_db_session()
    service = session.query(Service).get(data['service_id'])
    session.close()

    await state.update_data(selected_date=selected_date)
    await state.set_state(BookingStates.waiting_for_time)

    await callback.message.edit_text(
        f"📅 Дата: {selected_date}\n⏱ Выберите время:",
        reply_markup=time_keyboard(selected_date, service.duration)
    )


@router.callback_query(F.data.startswith("time_"))
async def time_selected(callback: CallbackQuery, state: FSMContext):
    selected_time = callback.data.split('_')[1]
    data = await state.get_data()

    session = get_db_session()
    service = session.query(Service).get(data['service_id'])
    session.close()

    await state.update_data(selected_time=selected_time)
    await state.set_state(BookingStates.waiting_for_confirmation)

    from datetime import datetime
    appointment_datetime = datetime.strptime(
        f"{data['selected_date']} {selected_time}",
        '%Y-%m-%d %H:%M'
    )

    confirmation_text = (
        f"📋 Подтвердите запись:\n\n"
        f"• Услуга: {service.name}\n"
        f"• Дата: {appointment_datetime.strftime('%d.%m.%Y')}\n"
        f"• Время: {appointment_datetime.strftime('%H:%M')}\n"
        f"• Цена: {service.price}₽\n"
        f"• Длительность: {service.duration} мин."
    )

    await callback.message.edit_text(
        confirmation_text,
        reply_markup=confirm_keyboard()
    )


@router.callback_query(F.data == "confirm_booking")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # session = get_db_session()
    with get_db_session() as session:
        service = session.query(Service).get(data['service_id'])
        user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()

        from datetime import datetime
        appointment_datetime = datetime.strptime(
            f"{data['selected_date']} {data['selected_time']}",
            '%Y-%m-%d %H:%M'
        )

        appointment = Appointment(
            user_id=user.id,
            service_id=service.id,
            appointment_time=appointment_datetime,
            status='confirmed'
        )

        session.add(appointment)
        session.commit()
        # session.close()

        await callback.message.edit_text(
            "✅ Запись успешно оформлена!\n\n"
            f"📋 Услуга: {service.name}\n"
            f"📅 Дата: {appointment_datetime.strftime('%d.%m.%Y %H:%M')}\n"
            f"💵 Стоимость: {service.price}₽\n\n"
            "Мы ждем вас! 🎉"
        )

    # Оповещение администратора
    for admin_id in config.ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"📋 Новая запись!\n\n"
                f"👤 Клиент: {user.first_name} {user.last_name}\n"
                f"📞 Username: @{user.username}\n"
                f"🎯 Услуга: {service.name}\n"
                f"📅 Время: {appointment_datetime.strftime('%d.%m.%Y %H:%M')}"
            )
        except:
            pass

    await state.clear()


@router.callback_query(F.data == "cancel_booking")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Запись отменена",
        reply_markup=services_keyboard()
    )

@router.callback_query(F.data == "delete_app")
async def delete_booking(callback: CallbackQuery, state: FSMContext):
    # await state.clear()
    await callback.message.edit_text(
        "❌ Запись отменена",
        reply_markup=services_keyboard()
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    # Для возврата в главное меню используем answer вместо edit_text,
    # так как нужно сменить тип клавиатуры с inline на reply
    await callback.message.delete()  # Удаляем предыдущее сообщение с инлайн-кнопками
    await callback.message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard()
    )


@router.callback_query(F.data == "back_to_services")
async def back_to_services(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BookingStates.waiting_for_service)
    await callback.message.edit_text(
        "🎯 Выберите услугу:",
        reply_markup=services_keyboard()
    )


@router.callback_query(F.data == "back_to_dates")
async def back_to_dates(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BookingStates.waiting_for_date)
    await callback.message.edit_text(
        "📅 Выберите дату:",
        reply_markup=date_keyboard()
    )