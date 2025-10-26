"""
Utils Module

Вспомогательные функции для Telegram бота.

Author: Vladimir
Date: 2024-10-26
"""

from typing import Dict, Any


def get_day_name(day: int) -> str:
    """
    Получить название дня по номеру.
    
    Args:
        day: Номер дня (1-5)
        
    Returns:
        Название дня с типом заданий
        
    Example:
        >>> name = get_day_name(1)
        >>> print(name)  # "Grammar (Грамматика)"
    """
    day_names = {
        1: "Grammar (Грамматика)",
        2: "Reading (Чтение)",
        3: "Vocabulary (Словарный запас)",
        4: "Situations (Жизненные ситуации)",
        5: "Review (Повторение)"
    }
    return day_names.get(day, f"День {day}")


def format_progress_message(
    current_day: int,
    task_in_day: int,
    theme_name: str,
    completed_today: int
) -> str:
    """
    Форматировать сообщение о прогрессе пользователя.
    
    Args:
        current_day: Текущий день (1-5)
        task_in_day: Номер задания в дне (1-3)
        theme_name: Название темы
        completed_today: Количество выполненных заданий сегодня
        
    Returns:
        Отформатированная строка с прогрессом
        
    Example:
        >>> msg = format_progress_message(2, 1, "Family and Friends", 0)
        >>> print(msg)
    """
    day_name = get_day_name(current_day)
    
    message = (
        f"📍 <b>Текущая позиция</b>\n"
        f"📚 Тема: <b>{theme_name}</b>\n"
        f"📅 День: <b>{current_day}/5</b> - {day_name}\n"
        f"📝 Задание: <b>{task_in_day}/3</b>\n\n"
        f"📈 <b>Сегодня</b>\n"
        f"✅ Выполнено: {completed_today}/3\n"
        f"⏳ Осталось: {max(0, 3 - completed_today)}/3"
    )
    
    return message


def format_statistics(stats: Dict[str, Any]) -> str:
    """
    Форматировать детальную статистику пользователя.
    
    Args:
        stats: Словарь со статистикой из get_user_stats()
        
    Returns:
        Отформатированная строка со статистикой
        
    Example:
        >>> stats = db.get_user_stats(user_id)
        >>> msg = format_statistics(stats)
        >>> await message.answer(msg, parse_mode="HTML")
    """
    message = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"📚 <b>Уровень:</b> {stats['level']}\n"
        f"📖 <b>Текущая тема:</b> {stats['current_theme'] or 'Не начата'}\n"
        f"📅 <b>День:</b> {stats['current_day']}/5\n"
        f"📝 <b>Задание:</b> {stats['task_in_day']}/3\n\n"
        f"✅ <b>Всего выполнено:</b> {stats['total_tasks_completed']} заданий\n"
        f"🎯 <b>Правильных ответов:</b> {stats['correct_tasks']}\n"
        f"❌ <b>Неправильных ответов:</b> {stats['incorrect_tasks']}\n"
        f"📊 <b>Точность:</b> {stats['accuracy']:.1f}%\n"
    )
    
    # Добавляем информацию о непроверенных ответах
    if stats['unchecked_open_answers'] > 0:
        message += f"\n⏳ <b>Ответов на проверке:</b> {stats['unchecked_open_answers']}"
    
    return message


def format_task_message(
    task_id: str,
    theme_name: str,
    current_day: int,
    task_in_day: int,
    question: str
) -> str:
    """
    Форматировать сообщение с заданием.
    
    Args:
        task_id: ID задания
        theme_name: Название темы
        current_day: Текущий день
        task_in_day: Номер задания в дне
        question: Текст вопроса
        
    Returns:
        Отформатированное сообщение с заданием
        
    Example:
        >>> msg = format_task_message(
        ...     "BEG-FAM-D1-G1",
        ...     "Family and Friends",
        ...     1, 1,
        ...     "This is ___ book."
        ... )
    """
    day_name = get_day_name(current_day)
    
    message = (
        f"📚 <b>Тема:</b> {theme_name}\n"
        f"📅 <b>День {current_day}/5</b> - {day_name}\n"
        f"📝 <b>Задание {task_in_day}/3</b>\n\n"
        f"❓ <b>Вопрос:</b>\n{question}"
    )
    
    return message


def format_day_completion_message(
    completed_today: int,
    accuracy: float,
    next_day: int
) -> str:
    """
    Форматировать сообщение о завершении дня.
    
    Args:
        completed_today: Количество выполненных заданий
        accuracy: Точность ответов (%)
        next_day: Номер следующего дня
        
    Returns:
        Отформатированное сообщение
        
    Example:
        >>> msg = format_day_completion_message(3, 66.7, 2)
    """
    next_day_name = get_day_name(next_day)
    
    message = (
        f"🎉 <b>Отлично! День завершен!</b>\n\n"
        f"📊 <b>Статистика за день:</b>\n"
        f"✅ Выполнено заданий: {completed_today}\n"
        f"🎯 Точность: {accuracy:.1f}%\n\n"
        f"📅 <b>Завтра:</b> День {next_day}/5\n"
        f"📖 Тип заданий: {next_day_name}\n\n"
        f"🌙 Увидимся завтра! Напишу в 9:00 ⏰"
    )
    
    return message


def format_theme_completion_message(
    theme_name: str,
    total_tasks: int,
    accuracy: float,
    next_theme_name: str = None
) -> str:
    """
    Форматировать сообщение о завершении темы.
    
    Args:
        theme_name: Название завершенной темы
        total_tasks: Количество выполненных заданий
        accuracy: Общая точность по теме
        next_theme_name: Название следующей темы (если есть)
        
    Returns:
        Отформатированное сообщение
        
    Example:
        >>> msg = format_theme_completion_message(
        ...     "Family and Friends",
        ...     15,
        ...     85.5,
        ...     "Daily Routine"
        ... )
    """
    message = (
        f"🎊 <b>Поздравляем! Тема завершена!</b>\n\n"
        f"📖 <b>Тема:</b> {theme_name}\n"
        f"✅ <b>Выполнено:</b> {total_tasks} заданий за 5 дней\n"
        f"🎯 <b>Общая точность:</b> {accuracy:.1f}%\n\n"
    )
    
    if next_theme_name:
        message += (
            f"🚀 <b>Следующая тема:</b> {next_theme_name}\n"
            f"🔔 Напишу завтра в 9:00!"
        )
    else:
        message += (
            f"🎓 <b>Поздравляем!</b> Вы завершили все темы этого уровня!\n"
            f"💡 Рекомендуем перейти на следующий уровень: /changelevel"
        )
    
    return message

