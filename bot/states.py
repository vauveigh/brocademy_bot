"""
Bot States Module

Определение FSM (Finite State Machine) состояний для Telegram бота.
Используется для управления диалоговым потоком и отслеживания контекста пользователя.

Author: Vladimir
Date: 2024-10-26
"""

from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """
    Состояния пользователя в процессе взаимодействия с ботом.
    
    Используется aiogram FSM (Finite State Machine) для управления
    многошаговыми диалогами и отслеживания текущего контекста.
    
    States:
        idle: Пользователь в ожидании команды (начальное состояние)
        waiting_for_level: Ожидание выбора уровня сложности
        waiting_for_answer: Ожидание ответа на задание (multiple choice)
        waiting_for_text_answer: Ожидание текстового ответа (open question)
        waiting_for_level_change_confirm: Ожидание подтверждения смены уровня
        
    Example:
        >>> from aiogram.fsm.context import FSMContext
        >>> # Установить состояние
        >>> await state.set_state(UserStates.waiting_for_answer)
        >>> # Получить текущее состояние
        >>> current_state = await state.get_state()
        >>> # Очистить состояние
        >>> await state.clear()
    """
    
    # Начальное состояние - пользователь в режиме ожидания команды
    idle = State()
    
    # Выбор уровня сложности при регистрации
    waiting_for_level = State()
    
    # Ожидание ответа на задание с multiple choice
    waiting_for_answer = State()
    
    # Ожидание текстового ответа на открытый вопрос
    waiting_for_text_answer = State()
    
    # Ожидание подтверждения смены уровня
    waiting_for_level_change_confirm = State()


# Константы для callback_data
class CallbackData:
    """
    Константы для callback_data кнопок.
    
    Используются для идентификации действий пользователя
    при нажатии на inline кнопки.
    """
    
    # Выбор уровня
    LEVEL_BEGINNER = "level:Beginner"
    LEVEL_ELEMENTARY = "level:Elementary"
    LEVEL_ADVANCED = "level:Advanced"
    
    # Начало заданий
    START_TASKS = "start_tasks"
    CONTINUE_TASKS = "continue_tasks"
    
    # Смена уровня
    CHANGE_LEVEL_CONFIRM = "change_level:confirm"
    CHANGE_LEVEL_CANCEL = "change_level:cancel"
    
    # Префиксы для динамических callback
    ANSWER_PREFIX = "answer:"  # answer:option_text
    LEVEL_PREFIX = "level:"    # level:Level_name


def get_level_from_callback(callback_data: str) -> str:
    """
    Извлечь уровень из callback_data.
    
    Args:
        callback_data: Строка вида "level:Beginner"
        
    Returns:
        Название уровня (например, "Beginner")
        
    Example:
        >>> level = get_level_from_callback("level:Elementary")
        >>> print(level)  # "Elementary"
    """
    if callback_data.startswith(CallbackData.LEVEL_PREFIX):
        return callback_data.split(":", 1)[1]
    return ""


def get_answer_from_callback(callback_data: str) -> str:
    """
    Извлечь ответ из callback_data.
    
    Args:
        callback_data: Строка вида "answer:my"
        
    Returns:
        Текст ответа
        
    Example:
        >>> answer = get_answer_from_callback("answer:my")
        >>> print(answer)  # "my"
    """
    if callback_data.startswith(CallbackData.ANSWER_PREFIX):
        return callback_data.split(":", 1)[1]
    return ""

