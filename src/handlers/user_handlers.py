from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import get_db_session, User, Appointment
from keyboards import main_menu_keyboard, services_keyboard, admin_keyboard
from states import BookingStates
from src import config

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    session = get_db_session()

    db_user = session.query(User).filter(User.telegram_id == message.from_user.id).first()

    if not db_user:
        db_user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        session.add(db_user)
        session.commit()

    session.close()
    if message.from_user.id in config.ADMIN_IDS:
        welcome_text = (
            f"👋 Добро пожаловать, {message.from_user.first_name}! Вы являетесь администратором!\n\n"
            "Я бот для записи на услуги. Вот что я могу:\n"
            "• 📊 Показать статистику\n"
            "• ➕ Добавить услугу\n"
            "• ✏️ Редактировать услуги\n"
            "• 📅 Управление записями\n\n"
            "Выберите действие:"
        )

        await message.answer(welcome_text, reply_markup=admin_keyboard())
    else:
        welcome_text = (
            f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
            "Я бот для записи на услуги. Вот что я могу:\n"
            "• 📋 Показать доступные услуги\n"
            "• 📅 Записать вас на прием\n"
            "• 📝 Показать ваши записи\n"
            "• ⚙️ Настроить профиль\n\n"
            "Выберите действие:"
        )

        await message.answer(welcome_text, reply_markup=main_menu_keyboard())


@router.message(F.text == "📋 Услуги и запись")
async def show_services(message: Message, state: FSMContext):
    await state.set_state(BookingStates.waiting_for_service)
    await message.answer("🎯 Выберите услугу:", reply_markup=services_keyboard())


@router.message(F.text == "📅 Мои записи")
async def show_my_appointments(message: Message):
    session = get_db_session()
    user = session.query(User).filter(User.telegram_id == message.from_user.id).first()

    if user:
        from datetime import datetime
        appointments = session.query(Appointment).filter(
            Appointment.user_id == user.id,
            Appointment.appointment_time >= datetime.now()
        ).order_by(Appointment.appointment_time).all()

        if appointments:
            text = "📅 Ваши ближайшие записи:\n\n"
            for app in appointments:
                text += (
                    f"• {app.service.name} - {app.appointment_time.strftime('%d.%m.%Y %H:%M')}\n"
                    f"  Статус: {app.status}\n"
                    f"  Цена: {app.service.price}₽\n\n"
                )
        else:
            text = "📭 У вас нет предстоящих записей"
    else:
        text = "❌ Пользователь не найден"

    session.close()
    await message.answer(text)


@router.message(F.text == "📞 Контакты")
async def show_contacts(message: Message):
    contacts_text = (
        "📞 Контакты:\n\n"
        "📍 Адрес: ул. Примерная, д. 123\n"
        "📱 Телефон: +7 (999) 123-45-67\n"
        "🕒 Часы работы: Пн-Пт 9:00-21:00\n\n"
        "Свяжитесь с нами для уточнения деталей!"
    )
    await message.answer(contacts_text)


@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: Message):
    settings_text = (
        "⚙️ Настройки профиля:\n\n"
        "Здесь вы можете:\n"
        "• Изменить контактные данные\n"
        "• Настроить уведомления\n"
        "• Посмотреть историю записей\n\n"
        "Функционал в разработке 🛠"
    )
    await message.answer(settings_text)


@router.message(F.text == "⬅️ В главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await cmd_start(message)


@router.message(F.text.in_(["📊 Статистика", "➕ Добавить услугу", "✏️ Редактировать услуги", "📅 Управление записями"]))
async def admin_actions(message: Message):
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer("Панель администратора:", reply_markup=admin_keyboard())
    else:
        await message.answer("⛔ У вас нет прав администратора")