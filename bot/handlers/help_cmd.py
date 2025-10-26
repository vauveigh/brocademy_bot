"""
Help Handler

Обработчик команд /help, /about, /changelevel.

Author: Vladimir
Date: 2024-10-26
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config.config import config
from database.db_manager import DatabaseManager
from database.notion_client import get_notion_client
from bot.states import UserStates, CallbackData, get_level_from_callback
from bot.keyboards import (
    get_level_change_confirm_keyboard,
    get_level_selection_keyboard
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Обработчик команды /help - справка по командам бота.
    
    Args:
        message: Входящее сообщение
    """
    help_text = (
        "📚 <b>Справка по командам</b>\n\n"
        "<b>Основные команды:</b>\n"
        "/task - Получить текущее задание\n"
        "/progress - Посмотреть свой прогресс\n"
        "/my_answers - Мои открытые ответы\n"
        "/changelevel - Сменить уровень сложности\n"
        "/help - Эта справка\n"
        "/about - Информация о боте\n\n"
        "<b>💡 Как это работает:</b>\n\n"
        "📝 <b>3 задания в день</b>\n"
        "Каждый день вы получаете ровно 3 коротких задания (5-10 минут).\n"
        "После выполнения 3-го задания бот автоматически останавливается.\n\n"
        "📅 <b>5 дней = 1 тема</b>\n"
        "За 5 дней вы завершите одну тему (15 заданий):\n"
        "• День 1: Grammar (грамматика)\n"
        "• День 2: Reading (чтение)\n"
        "• День 3: Vocabulary (словарный запас)\n"
        "• День 4: Situations (жизненные ситуации)\n"
        "• День 5: Review (повторение)\n\n"
        "⏰ <b>Напоминания</b>\n"
        "Бот напишет вам каждый день в 9:00 утра.\n\n"
        "❓ <b>Типы заданий:</b>\n"
        "• <b>Multiple Choice</b> - выбор правильного ответа из вариантов\n"
        "• <b>Open Question</b> - текстовый ответ (проверяет преподаватель)\n\n"
        "💬 <b>Поддержка:</b>\n"
        "Если возникли вопросы, используйте /help или обратитесь к администратору."
    )
    
    await message.answer(help_text)
    logger.info(f"Help shown to user {message.from_user.id}")


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    """
    Обработчик команды /about - информация о боте.
    
    Args:
        message: Входящее сообщение
    """
    about_text = (
        "🤖 <b>English Learning Bot</b>\n\n"
        "Telegram-бот для ежедневной практики английского языка.\n\n"
        "<b>📌 Особенности:</b>\n"
        "• Структурированное обучение по темам\n"
        "• Постепенное повышение сложности\n"
        "• Регулярная практика (3 задания/день)\n"
        "• Автоматическая проверка ответов\n"
        "• Отслеживание прогресса\n"
        "• Поддержка медиа-контента\n\n"
        "<b>🎯 Уровни:</b>\n"
        "• Beginner (A1) - начальный\n"
        "• Elementary (A2) - элементарный\n"
        "• Advanced (B1-B2) - продвинутый\n\n"
        "<b>📊 Версия:</b> 1.0.0\n"
        "<b>👨‍💻 Автор:</b> Vladimir\n\n"
        "Спасибо, что учите английский с нами! 🇬🇧"
    )
    
    await message.answer(about_text)
    logger.info(f"About shown to user {message.from_user.id}")


@router.message(Command("changelevel"))
async def cmd_changelevel(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /changelevel - смена уровня сложности.
    
    Предупреждает о сбросе прогресса и запрашивает подтверждение.
    
    Args:
        message: Входящее сообщение
        state: FSM context
    """
    user_id = message.from_user.id
    db = DatabaseManager(config.SQLITE_DB_PATH)
    
    # Проверяем, зарегистрирован ли пользователь
    user = db.get_user(user_id)
    if not user:
        await message.answer(
            "❌ Вы не зарегистрированы!\n\n"
            "Используйте команду /start для регистрации."
        )
        return
    
    # Получаем текущий прогресс
    stats = db.get_user_stats(user_id)
    
    warning_text = (
        "⚠️ <b>Внимание! Смена уровня сбросит ваш прогресс!</b>\n\n"
        f"<b>Текущий уровень:</b> {user['level']}\n"
        f"<b>Текущая тема:</b> {user['current_theme'] or 'Не начата'}\n"
        f"<b>День:</b> {user['current_day']}/5\n"
        f"<b>Задание:</b> {user['task_in_day']}/3\n\n"
        f"<b>Выполнено всего:</b> {stats['total_tasks_completed']} заданий\n"
        f"<b>Точность:</b> {stats['accuracy']:.1f}%\n\n"
        "При смене уровня вы начнете с самого начала (тема 1, день 1).\n\n"
        "<b>Вы уверены, что хотите сменить уровень?</b>"
    )
    
    await message.answer(
        warning_text,
        reply_markup=get_level_change_confirm_keyboard()
    )
    
    # Устанавливаем состояние ожидания подтверждения
    await state.set_state(UserStates.waiting_for_level_change_confirm)
    
    logger.info(f"Level change warning shown to user {user_id}")


@router.callback_query(
    F.data == CallbackData.CHANGE_LEVEL_CANCEL,
    UserStates.waiting_for_level_change_confirm
)
async def process_level_change_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка отмены смены уровня.
    
    Args:
        callback: Callback query
        state: FSM context
    """
    await callback.message.edit_text("❌ Смена уровня отменена")
    await callback.answer("Отменено")
    await state.clear()
    
    logger.info(f"Level change cancelled by user {callback.from_user.id}")


@router.callback_query(
    F.data == CallbackData.CHANGE_LEVEL_CONFIRM,
    UserStates.waiting_for_level_change_confirm
)
async def process_level_change_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка подтверждения смены уровня.
    
    Показывает выбор нового уровня.
    
    Args:
        callback: Callback query
        state: FSM context
    """
    await callback.message.edit_text(
        "🎯 <b>Выберите новый уровень:</b>",
        reply_markup=get_level_selection_keyboard()
    )
    
    await callback.answer()
    
    # Меняем состояние на ожидание выбора уровня
    await state.set_state(UserStates.waiting_for_level)
    
    logger.info(f"Level selection shown to user {callback.from_user.id}")


@router.callback_query(
    F.data.startswith(CallbackData.LEVEL_PREFIX),
    UserStates.waiting_for_level
)
async def process_new_level_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка выбора нового уровня после подтверждения смены.
    
    Args:
        callback: Callback query с новым уровнем
        state: FSM context
    """
    user_id = callback.from_user.id
    new_level = get_level_from_callback(callback.data)
    
    if not new_level:
        await callback.answer("❌ Ошибка выбора уровня")
        return
    
    # Обновляем уровень пользователя (сбрасывает прогресс)
    db = DatabaseManager(config.SQLITE_DB_PATH)
    
    try:
        success = db.update_user_level(user_id, new_level)
        
        if not success:
            await callback.answer("❌ Ошибка обновления уровня")
            return
        
        # Получаем информацию о первой теме нового уровня
        notion = get_notion_client()
        theme_info = notion.get_theme_info(new_level, 1)
        
        if theme_info:
            theme_name = theme_info['theme_name']
            db.update_user_progress(user_id, current_theme=theme_name)
        else:
            theme_name = "Первая тема"
        
        # Отправляем подтверждение
        success_text = (
            f"✅ <b>Уровень изменен на {new_level}!</b>\n\n"
            f"🔄 Прогресс сброшен. Начинаем с начала:\n"
            f"📖 Тема: {theme_name}\n"
            f"📅 День: 1/5\n"
            f"📝 Задание: 1/3\n\n"
            f"🚀 Готовы начать?\n"
            f"Используйте команду /task для получения первого задания."
        )
        
        await callback.message.edit_text(success_text)
        await callback.answer(f"Уровень изменен на {new_level}")
        await state.clear()
        
        logger.info(f"User {user_id} changed level to {new_level}")
        
    except Exception as e:
        logger.error(f"Error changing level for user {user_id}: {e}", exc_info=True)
        await callback.answer("❌ Ошибка изменения уровня")

