"""
Middlewares Module

Middleware для логирования и обработки запросов в Telegram боте.

Author: Vladimir
Date: 2024-10-26
"""

import logging
import time
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для логирования всех входящих сообщений и callback-запросов.
    
    Логирует:
    - User ID и username
    - Тип события (message/callback)
    - Содержимое сообщения или callback_data
    - Время обработки запроса
    
    Example:
        >>> dp.message.middleware(LoggingMiddleware())
        >>> dp.callback_query.middleware(LoggingMiddleware())
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработка события с логированием.
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Событие Telegram (Message или CallbackQuery)
            data: Дополнительные данные
            
        Returns:
            Результат выполнения handler
        """
        start_time = time.time()
        
        # Извлекаем информацию о пользователе
        user = None
        event_type = None
        event_data = None
        
        if isinstance(event, Message):
            user = event.from_user
            event_type = "message"
            event_data = event.text or event.caption or "<non-text>"
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            event_type = "callback"
            event_data = event.data
        
        # Логируем начало обработки
        if user:
            logger.info(
                f"📨 [{event_type}] User {user.id} (@{user.username or 'no_username'}): {event_data}"
            )
        
        try:
            # Выполняем handler
            result = await handler(event, data)
            
            # Логируем успешное завершение
            elapsed = time.time() - start_time
            logger.info(f"✅ [{event_type}] Processed in {elapsed:.2f}s")
            
            return result
            
        except Exception as e:
            # Логируем ошибку
            elapsed = time.time() - start_time
            logger.error(
                f"❌ [{event_type}] Error after {elapsed:.2f}s: {e}",
                exc_info=True
            )
            raise


class StateLoggingMiddleware(BaseMiddleware):
    """
    Middleware для логирования переходов между FSM состояниями.
    
    Полезно для отладки и понимания flow пользователя.
    
    Example:
        >>> dp.message.middleware(StateLoggingMiddleware())
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработка события с логированием состояний.
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Событие Telegram
            data: Дополнительные данные (включая FSM state)
            
        Returns:
            Результат выполнения handler
        """
        # Получаем FSM state из data
        state = data.get("state")
        
        if state:
            try:
                current_state = await state.get_state()
                if current_state:
                    logger.debug(f"🔄 Current FSM state: {current_state}")
            except Exception:
                pass
        
        # Выполняем handler
        result = await handler(event, data)
        
        # Проверяем изменилось ли состояние
        if state:
            try:
                new_state = await state.get_state()
                if new_state != current_state:
                    logger.info(f"🔄 FSM state changed: {current_state} → {new_state}")
            except Exception:
                pass
        
        return result


class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Middleware для обработки ошибок и отправки дружелюбных сообщений пользователю.
    
    При возникновении необработанного исключения:
    - Логирует детали ошибки
    - Отправляет пользователю дружелюбное сообщение
    - Уведомляет админа о критических ошибках
    - Не прерывает работу бота
    
    Example:
        >>> dp.message.middleware(ErrorHandlerMiddleware())
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработка события с обработкой ошибок.
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Событие Telegram
            data: Дополнительные данные
            
        Returns:
            Результат выполнения handler или None при ошибке
        """
        try:
            return await handler(event, data)
            
        except Exception as e:
            # Извлекаем информацию о пользователе и событии
            user = None
            event_type = "unknown"
            event_data = "N/A"
            
            if isinstance(event, Message):
                user = event.from_user
                event_type = "message"
                event_data = event.text or event.caption or "<non-text>"
            elif isinstance(event, CallbackQuery):
                user = event.from_user
                event_type = "callback"
                event_data = event.data
            
            # Логируем с полной информацией
            logger.error(
                f"❌ Unhandled error in {event_type} handler\n"
                f"User: {user.id if user else 'Unknown'} (@{user.username if user else 'Unknown'})\n"
                f"Event data: {event_data}\n"
                f"Error: {e}",
                exc_info=True
            )
            
            # Отправляем пользователю дружелюбное сообщение
            error_message = (
                "😔 Произошла ошибка при обработке вашего запроса.\n\n"
                "Попробуйте повторить действие или используйте /help для справки.\n"
                "Если проблема сохраняется, обратитесь в поддержку."
            )
            
            try:
                if isinstance(event, Message):
                    await event.answer(error_message)
                elif isinstance(event, CallbackQuery):
                    await event.message.answer(error_message)
                    await event.answer()  # Убираем "часики" на кнопке
            except Exception:
                # Даже если не удалось отправить сообщение, не падаем
                pass
            
            # Уведомляем админов о критической ошибке
            await self._notify_admins_about_error(event, e, user, event_type, event_data, data)
            
            return None
    
    async def _notify_admins_about_error(
        self,
        event: TelegramObject,
        error: Exception,
        user: Any,
        event_type: str,
        event_data: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Уведомить админов о критической ошибке.
        
        Args:
            event: Событие, вызвавшее ошибку
            error: Исключение
            user: Пользователь (если есть)
            event_type: Тип события
            event_data: Данные события
            data: Дополнительные данные
        """
        try:
            from config.config import config
            
            # Проверяем, есть ли админы в конфиге
            if not config.ADMIN_USER_IDS:
                return
            
            # Получаем бота из data
            bot = data.get("bot")
            if not bot:
                return
            
            # Формируем сообщение об ошибке
            import traceback
            
            error_report = (
                "🚨 <b>КРИТИЧЕСКАЯ ОШИБКА В БОТЕ</b>\n\n"
                f"<b>Тип события:</b> {event_type}\n"
                f"<b>Пользователь:</b> {user.id if user else 'Unknown'} "
                f"(@{user.username if user else 'Unknown'})\n"
                f"<b>Данные:</b> <code>{event_data[:100]}</code>\n\n"
                f"<b>Ошибка:</b>\n<code>{str(error)[:200]}</code>\n\n"
                f"<b>Traceback:</b>\n<code>{traceback.format_exc()[:500]}</code>"
            )
            
            # Отправляем всем админам
            for admin_id in config.ADMIN_USER_IDS:
                try:
                    await bot.send_message(admin_id, error_report)
                    logger.info(f"✉️ Error notification sent to admin {admin_id}")
                except Exception as send_error:
                    logger.error(f"Failed to notify admin {admin_id}: {send_error}")
                    
        except Exception as notify_error:
            # Если не удалось уведомить админов, просто логируем
            logger.error(f"Failed to notify admins: {notify_error}")

