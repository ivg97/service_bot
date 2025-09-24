from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from database import get_db_session, User, Appointment, Config, Service
from keyboards import main_menu_keyboard, services_keyboard, admin_keyboard, \
    cancel_appointment_keyboard, select_services_keyboard
from states import BookingStates
import config
from utils.decorators import is_admin

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
    with get_db_session() as session:
        user = session.query(User).filter(User.telegram_id == message.from_user.id).first()

        if user:
            from datetime import datetime
            appointments = session.query(Appointment).filter(
                Appointment.user_id == user.id,
                Appointment.appointment_time >= datetime.now()
            ).order_by(Appointment.appointment_time).all()

            if appointments:
                text = "📅 Выберите для подробного описания:\n\n"
            else:
                text = "📭 У вас нет предстоящих записей"
        else:
            text = "❌ Пользователь не найден"

        await message.answer(
            text,
            reply_markup=select_services_keyboard(appointments))



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
@is_admin
async def show_settings(message: Message):
    session = get_db_session()
    all_config = session.query(Config).all()
    text = f"⚙️ Текущие настройки:\n\n"
    for conf in all_config:
        text += f"{conf.name}: {conf.value}\n"
    session.close()
    settings_text = (
        "⚙️ Настройки профиля:\n\n"
        "Здесь вы можете:\n"
        "• Изменить контактные данные\n"
        "• Настроить уведомления\n"
        "• Посмотреть историю записей\n\n"
        "Функционал в разработке 🛠"
    )
    await message.answer(text)


@router.message(F.text == "✏️ Редактировать услуги")
@is_admin
async def edit_service(message: Message):
    session = get_db_session()
    all_services = session.query(Service).all()

    builder = InlineKeyboardBuilder()

    for service in all_services:
        builder.button(
            text=f"{service.name} - {service.price}₽",
            callback_data=f"edit_service_{service.id}"
        )

    builder.button(text="🔙 Назад", callback_data="admin_back")
    builder.adjust(1)

    # Отправляем сообщение с клавиатурой
    await message.answer(
        "⚙️ Выберите услугу для редактирования:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("edit_service_"))
@is_admin
async def handle_service_selection(callback):
    # Извлекаем ID услуги из callback_data
    service_id = int(callback.data.split("_")[2])

    session = get_db_session()
    service = session.query(Service).filter(Service.id == service_id).first()
    session.close()

    if not service:
        await callback.answer("Услуга не найдена!")
        return

    # Создаем клавиатуру для действий с выбранной услугой
    action_builder = InlineKeyboardBuilder()
    action_builder.button(text="✏️ Изменить название", callback_data=f"change_name_{service.id}")
    action_builder.button(text="💰 Изменить цену", callback_data=f"change_price_{service.id}")
    action_builder.button(text="🗑️ Удалить услугу", callback_data=f"delete_service_{service.id}")
    action_builder.button(text="🔙 Назад к списку", callback_data="back_to_services")
    action_builder.adjust(1)  # По одной кнопке в строке

    await callback.message.edit_text(
        f"📋 Редактирование услуги:\n\n"
        f"• Название: {service.name}\n"
        f"• Цена: {service.price}₽\n\n"
        f"Выберите действие:",
        reply_markup=action_builder.as_markup()
    )
    await callback.answer()

@router.message(F.text == "⬅️ В главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await cmd_start(message)


@router.message(F.text.in_(["✏️ Редактировать услуги", "📅 Управление записями"]))
@is_admin
async def admin_actions(message: Message):
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer("Панель администратора:", reply_markup=admin_keyboard())
    else:
        await message.answer("⛔ У вас нет прав администратора")
