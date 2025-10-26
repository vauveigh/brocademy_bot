"""
Keyboards Module

Inline клавиатуры для Telegram бота.
Все клавиатуры вынесены в отдельный модуль для удобства поддержки.

Author: Vladimir
Date: 2024-10-26
"""

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.states import CallbackData


def get_level_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора уровня сложности.
    
    Отображается при регистрации пользователя или при смене уровня.
    
    Returns:
        InlineKeyboardMarkup с тремя кнопками уровней
        
    Example:
        >>> keyboard = get_level_selection_keyboard()
        >>> await message.answer("Выберите уровень:", reply_markup=keyboard)
    """
    buttons = [
        [InlineKeyboardButton(
            text="🟢 Beginner (A1)",
            callback_data=CallbackData.LEVEL_BEGINNER
        )],
        [InlineKeyboardButton(
            text="🟡 Elementary (A2)",
            callback_data=CallbackData.LEVEL_ELEMENTARY
        )],
        [InlineKeyboardButton(
            text="🔴 Advanced (B1-B2)",
            callback_data=CallbackData.LEVEL_ADVANCED
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_start_tasks_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для начала выполнения заданий.
    
    Отображается после успешной регистрации.
    
    Returns:
        InlineKeyboardMarkup с кнопкой "Начать"
        
    Example:
        >>> keyboard = get_start_tasks_keyboard()
        >>> await message.answer("Готовы начать?", reply_markup=keyboard)
    """
    buttons = [
        [InlineKeyboardButton(
            text="🚀 Начать первое задание!",
            callback_data=CallbackData.START_TASKS
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_continue_tasks_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для продолжения выполнения заданий.
    
    Отображается при повторном /start для зарегистрированного пользователя.
    
    Returns:
        InlineKeyboardMarkup с кнопкой "Продолжить"
        
    Example:
        >>> keyboard = get_continue_tasks_keyboard()
        >>> await message.answer("Рад снова тебя видеть!", reply_markup=keyboard)
    """
    buttons = [
        [InlineKeyboardButton(
            text="▶️ Продолжить",
            callback_data=CallbackData.CONTINUE_TASKS
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_answer_options_keyboard(options: List[str]) -> InlineKeyboardMarkup:
    """
    Клавиатура с вариантами ответов для multiple choice задания.
    
    Args:
        options: Список вариантов ответа (обычно 4 варианта)
        
    Returns:
        InlineKeyboardMarkup с кнопками вариантов (2 в ряд)
        
    Example:
        >>> options = ["my", "mine", "me", "I"]
        >>> keyboard = get_answer_options_keyboard(options)
        >>> await message.answer("Choose the correct answer:", reply_markup=keyboard)
    """
    buttons = []
    
    # Размещаем кнопки по 2 в ряд
    for i in range(0, len(options), 2):
        row = []
        
        # Первая кнопка в ряду
        row.append(InlineKeyboardButton(
            text=options[i],
            callback_data=f"{CallbackData.ANSWER_PREFIX}{options[i]}"
        ))
        
        # Вторая кнопка в ряду (если есть)
        if i + 1 < len(options):
            row.append(InlineKeyboardButton(
                text=options[i + 1],
                callback_data=f"{CallbackData.ANSWER_PREFIX}{options[i + 1]}"
            ))
        
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_level_change_confirm_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для подтверждения смены уровня.
    
    Отображается при выполнении команды /changelevel.
    Предупреждает о сбросе прогресса.
    
    Returns:
        InlineKeyboardMarkup с кнопками подтверждения и отмены
        
    Example:
        >>> keyboard = get_level_change_confirm_keyboard()
        >>> await message.answer("Уверены?", reply_markup=keyboard)
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Да, сменить уровень",
                callback_data=CallbackData.CHANGE_LEVEL_CONFIRM
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=CallbackData.CHANGE_LEVEL_CANCEL
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def remove_keyboard() -> InlineKeyboardMarkup:
    """
    Пустая клавиатура для удаления кнопок.
    
    Используется после ответа на задание, чтобы нельзя было
    изменить ответ повторным нажатием.
    
    Returns:
        Пустая InlineKeyboardMarkup
        
    Example:
        >>> await message.edit_reply_markup(reply_markup=remove_keyboard())
    """
    return InlineKeyboardMarkup(inline_keyboard=[])

