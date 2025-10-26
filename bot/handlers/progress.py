"""
Progress Handler

Обработчик команд /progress и /my_answers - статистика и открытые ответы пользователя.

Author: Vladimir
Date: 2024-10-26
"""

import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config.config import config
from database.db_manager import DatabaseManager
from bot.utils import format_statistics

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("progress"))
async def cmd_progress(message: Message) -> None:
    """
    Обработчик команды /progress - показать статистику пользователя.
    
    Отображает:
    - Текущую позицию (тема, день, задание)
    - Прогресс за сегодня
    - Общую статистику (выполнено заданий, точность)
    - Статистику по типам заданий
    
    Args:
        message: Входящее сообщение
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
    
    # Получаем статистику
    stats = db.get_user_stats(user_id)
    
    if not stats:
        await message.answer("❌ Не удалось получить статистику")
        return
    
    # Получаем прогресс за сегодня
    day_progress = db.get_current_day_progress(user_id)
    
    # Форматируем сообщение
    stats_message = format_statistics(stats)
    
    # Добавляем прогресс за сегодня
    if day_progress:
        stats_message += (
            f"\n\n📈 <b>Сегодня:</b>\n"
            f"✅ Выполнено: {day_progress['completed_today']}/3\n"
            f"⏳ Осталось: {day_progress['remaining_today']}/3"
        )
    
    # Получаем детальную статистику по типам
    progress_stats = db.get_user_progress_stats(user_id)
    
    if progress_stats and progress_stats['by_type']:
        stats_message += "\n\n📚 <b>По типам заданий:</b>\n"
        
        type_names = {
            'grammar': '📝 Grammar',
            'reading': '📖 Reading',
            'vocabulary': '💬 Vocabulary',
            'situations': '🗣️ Situations',
            'review': '🔄 Review'
        }
        
        for task_type, type_stats in progress_stats['by_type'].items():
            type_name = type_names.get(task_type, task_type)
            stats_message += (
                f"{type_name}: {type_stats['correct']}/{type_stats['total']} "
                f"({type_stats['accuracy']:.1f}%)\n"
            )
    
    await message.answer(stats_message)
    logger.info(f"Progress shown to user {user_id}")


@router.message(Command("my_answers"))
async def cmd_my_answers(message: Message) -> None:
    """
    Обработчик команды /my_answers - показать открытые ответы пользователя.
    
    Отображает:
    - Ответы, ожидающие проверки
    - Проверенные ответы
    
    Args:
        message: Входящее сообщение
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
    
    # Получаем все открытые ответы пользователя
    unchecked = db.get_user_open_answers(user_id, checked=False)
    checked = db.get_user_open_answers(user_id, checked=True)
    
    if not unchecked and not checked:
        await message.answer(
            "📝 <b>У вас пока нет открытых ответов</b>\n\n"
            "Открытые ответы появляются при выполнении заданий типа "
            "\"открытый вопрос\", которые требуют текстового ответа."
        )
        return
    
    # Формируем сообщение
    response = "📝 <b>Ваши открытые ответы</b>\n\n"
    
    # Непроверенные ответы
    if unchecked:
        response += f"⏳ <b>Ожидают проверки: {len(unchecked)}</b>\n\n"
        
        for i, answer in enumerate(unchecked[:5], 1):  # Показываем максимум 5
            question_short = (
                answer['question'][:50] + "..."
                if len(answer['question']) > 50
                else answer['question']
            )
            response += (
                f"{i}. <b>{answer['task_id']}</b>\n"
                f"   ❓ {question_short}\n"
                f"   ✍️ Ваш ответ: {answer['user_answer'][:60]}...\n"
                f"   📅 {answer['created_at'][:10]}\n\n"
            )
        
        if len(unchecked) > 5:
            response += f"   ... и еще {len(unchecked) - 5}\n\n"
    
    # Проверенные ответы
    if checked:
        response += f"✅ <b>Проверено: {len(checked)}</b>\n\n"
        
        for i, answer in enumerate(checked[:3], 1):  # Показываем максимум 3
            question_short = (
                answer['question'][:50] + "..."
                if len(answer['question']) > 50
                else answer['question']
            )
            response += (
                f"{i}. <b>{answer['task_id']}</b>\n"
                f"   ❓ {question_short}\n"
                f"   📅 {answer['created_at'][:10]}\n\n"
            )
        
        if len(checked) > 3:
            response += f"   ... и еще {len(checked) - 3}\n\n"
    
    await message.answer(response)
    logger.info(f"Open answers shown to user {user_id}")

