from functools import wraps
from aiogram.types import CallbackQuery, Message
from typing import Union, Callable

import config


def is_admin(func: Callable):
    """
    Декоратор для проверки прав администратора.
    Если пользователь не админ - отвечаем на callback и останавливаем обработку.
    """

    @wraps(func)
    async def wrapper(update: Union[CallbackQuery, Message], *args, **kwargs):
        # Определяем ID пользователя в зависимости от типа update
        user_id = update.from_user.id

        if user_id not in config.ADMIN_IDS:
            # Если это callback (нажатие inline-кнопки)
            if isinstance(update, CallbackQuery):
                await update.answer("❌ У вас нет прав для этого действия!", show_alert=True)
                return
            # Если это обычное сообщение
            elif isinstance(update, Message):
                await update.answer("❌ У вас нет прав для этого действия!")
                return

        # Если пользователь админ - вызываем оригинальную функцию
        return await func(update, *args, **kwargs)

    return wrapper