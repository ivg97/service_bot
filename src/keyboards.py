from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from datetime import datetime, timedelta
from database import get_db_session, Service, Appointment
import config


def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 Услуги и запись")
    builder.button(text="📅 Мои записи")
    builder.button(text="📞 Контакты")
    builder.button(text="⚙️ Настройки")
    builder.adjust(1, 2, 1)
    return builder.as_markup(resize_keyboard=True)


def services_keyboard():
    session = get_db_session()
    services = session.query(Service).filter(Service.is_active == True).all()
    session.close()

    builder = InlineKeyboardBuilder()
    for service in services:
        builder.button(
            text=f"{service.name} - {service.price}₽",
            callback_data=f"service_{service.id}"
        )

    builder.button(text="⬅️ Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def date_keyboard():
    builder = InlineKeyboardBuilder()
    today = datetime.now().date()

    for i in range(7):
        date = today + timedelta(days=i)
        if date.weekday() < 5:
            builder.button(
                text=date.strftime("%d.%m (%a)"),
                callback_data=f"date_{date.strftime('%Y-%m-%d')}"
            )

    builder.button(text="⬅️ Назад", callback_data="back_to_services")
    builder.adjust(2)
    return builder.as_markup()


def time_keyboard(selected_date, service_duration):
    builder = InlineKeyboardBuilder()
    start_time = datetime.strptime(selected_date, '%Y-%m-%d').replace(
        hour=config.WORKING_HOURS['start'],
        minute=0
    )
    end_time = datetime.strptime(selected_date, '%Y-%m-%d').replace(
        hour=config.WORKING_HOURS['end'],
        minute=0
    )

    session = get_db_session()
    current_time = start_time

    while current_time + timedelta(minutes=service_duration) <= end_time:
        existing_appointments = session.query(Appointment).filter(
            Appointment.appointment_time >= current_time,
            Appointment.appointment_time < current_time + timedelta(minutes=service_duration),
            Appointment.status.in_(['pending', 'confirmed'])
        ).count()

        if existing_appointments == 0:
            builder.button(
                text=current_time.strftime("%H:%M"),
                callback_data=f"time_{current_time.strftime('%H:%M')}"
            )

        current_time += timedelta(minutes=30)

    session.close()

    builder.button(text="⬅️ Назад", callback_data="back_to_dates")
    builder.adjust(4)
    return builder.as_markup()


def confirm_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="confirm_booking")
    builder.button(text="❌ Отменить", callback_data="cancel_booking")
    builder.adjust(2)
    return builder.as_markup()


def admin_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📊 Статистика")
    builder.button(text="➕ Добавить услугу")
    builder.button(text="✏️ Редактировать услуги")
    builder.button(text="📅 Управление записями")
    builder.button(text="⬅️ В главное меню")
    builder.adjust(1, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


def back_to_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В главное меню", callback_data="back_to_main")
    return builder.as_markup()


def back_to_main_inline_keyboard():
    """Инлайн клавиатура для возврата в главное меню (для использования с edit_text)"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В главное меню", callback_data="back_to_main")
    return builder.as_markup()