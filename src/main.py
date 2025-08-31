import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import BotCommand

from config import TOKEN, ADMIN_IDS
from database import init_db
from handlers import user_handlers, callback_handlers, admin_handlers


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)


async def main():
    # Инициализация базы данных
    init_db()

    # Создание бота и диспетчера
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    # Регистрация роутеров
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(callback_handlers.router)


    # Установка команд бота
    await set_bot_commands(bot)

    # Запуск бота
    logging.info("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())