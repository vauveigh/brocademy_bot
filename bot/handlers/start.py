"""
Start Handler

Обработчик команды /start - регистрация и онбординг новых пользователей.

Author: Vladimir
Date: 2024-10-26
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from config.config import config
from database.db_manager import DatabaseManager
from database.notion_client import get_notion_client
from bot.states import UserStates, CallbackData, get_level_from_callback
from bot.keyboards import (
    get_level_selection_keyboard,
    get_start_tasks_keyboard,
    get_continue_tasks_keyboard
)
from bot.utils import format_progress_message

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /start.
    
    Если пользователь НЕ зарегистрирован:
    - Показывает приветственное сообщение
    - Предлагает выбрать уровень сложности
    
    Если пользователь УЖЕ зарегистрирован:
    - Показывает текущий прогресс
    - Предлагает продолжить обучение
    
    Args:
        message: Входящее сообщение
        state: FSM context для управления состоянием
    """
    user_id = message.from_user.id
    username = message.from_user.username
    
    db = DatabaseManager(config.SQLITE_DB_PATH)
    user = db.get_user(user_id)
    
    if user is None:
        # Новый пользователь - показываем онбординг
        await show_onboarding(message, state)
    else:
        # Существующий пользователь - показываем прогресс
        await show_returning_user(message, state, user)


async def show_onboarding(message: Message, state: FSMContext) -> None:
    """
    Показать онбординг для нового пользователя.
    
    Args:
        message: Входящее сообщение
        state: FSM context
    """
    welcome_text = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        f"Я помогу тебе практиковать английский каждый день! 🇬🇧\n\n"
        f"<b>📚 Как это работает:</b>\n"
        f"• <b>3 задания в день</b> (5-10 минут)\n"
        f"• <b>5 дней</b> = 1 тема (15 заданий)\n"
        f"• Каждый день — свой тип заданий:\n"
        f"  День 1: Grammar (грамматика)\n"
        f"  День 2: Reading (чтение)\n"
        f"  День 3: Vocabulary (словарный запас)\n"
        f"  День 4: Situations (ситуации)\n"
        f"  День 5: Review (повторение)\n\n"
        f"• После 3-го задания — автоматическая остановка\n"
        f"• Утреннее напоминание в 9:00 ⏰\n\n"
        f"<b>🎯 Выбери свой уровень:</b>"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_level_selection_keyboard()
    )
    
    # Устанавливаем состояние ожидания выбора уровня
    await state.set_state(UserStates.waiting_for_level)
    
    logger.info(f"Onboarding shown to user {message.from_user.id}")


async def show_returning_user(message: Message, state: FSMContext, user: dict) -> None:
    """
    Показать информацию для вернувшегося пользователя.
    
    Args:
        message: Входящее сообщение
        state: FSM context
        user: Данные пользователя из БД
    """
    db = DatabaseManager(config.SQLITE_DB_PATH)
    progress = db.get_current_day_progress(user['user_id'])
    
    welcome_back_text = (
        f"👋 Рад снова тебя видеть, <b>{message.from_user.first_name}</b>!\n\n"
    )
    
    # Добавляем информацию о прогрессе
    if progress:
        progress_msg = format_progress_message(
            progress['current_day'],
            progress['task_in_day'],
            progress['current_theme'] or "Начальная тема",
            progress['completed_today']
        )
        welcome_back_text += progress_msg
    else:
        welcome_back_text += (
            f"📚 <b>Уровень:</b> {user['level']}\n"
            f"📖 <b>Тема:</b> {user['current_theme'] or 'Не начата'}\n"
        )
    
    # Проверяем, выполнил ли пользователь задания на сегодня
    if progress and progress['completed_today'] >= 3:
        welcome_back_text += (
            f"\n\n✅ <b>Вы уже выполнили все задания на сегодня!</b>\n"
            f"🌙 Увидимся завтра в 9:00!"
        )
        keyboard = None
    else:
        welcome_back_text += f"\n\n💡 Готовы продолжить?"
        keyboard = get_continue_tasks_keyboard()
    
    await message.answer(
        welcome_back_text,
        reply_markup=keyboard
    )
    
    # Сбрасываем состояние (пользователь в режиме idle)
    await state.clear()
    
    logger.info(f"Returning user {message.from_user.id} greeted")


@router.callback_query(F.data.startswith(CallbackData.LEVEL_PREFIX))
async def process_level_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка выбора уровня сложности.
    
    Args:
        callback: Callback query с выбранным уровнем
        state: FSM context
    """
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    # Извлекаем выбранный уровень
    level = get_level_from_callback(callback.data)
    
    if not level:
        await callback.answer("❌ Ошибка выбора уровня")
        return
    
    # Создаем пользователя в БД
    db = DatabaseManager(config.SQLITE_DB_PATH)
    
    try:
        created = db.create_user(user_id, username, level)
        
        if not created:
            # Пользователь уже существует (не должно произойти, но на всякий случай)
            await callback.answer("Вы уже зарегистрированы!")
            return
        
        # Получаем информацию о первой теме из Notion
        notion = get_notion_client()
        theme_info = notion.get_theme_info(level, 1)
        
        if theme_info:
            theme_name = theme_info['theme_name']
            
            # Обновляем текущую тему в БД
            db.update_user_progress(
                user_id,
                current_theme=theme_name
            )
        else:
            theme_name = "Первая тема"
            logger.warning(f"Theme info not found for {level}, theme_order=1")
        
        # Формируем сообщение о успешной регистрации
        success_text = (
            f"✅ <b>Отлично! Вы зарегистрированы!</b>\n\n"
            f"📚 <b>Ваш уровень:</b> {level}\n"
            f"📖 <b>Первая тема:</b> {theme_name}\n\n"
            f"🎯 Вы будете проходить <b>3 задания в день</b>\n"
            f"📅 За <b>5 дней</b> завершите тему (15 заданий)\n\n"
            f"🚀 Готовы начать?"
        )
        
        # Удаляем предыдущее сообщение с выбором уровня
        await callback.message.edit_text(
            success_text,
            reply_markup=get_start_tasks_keyboard()
        )
        
        # Убираем состояние ожидания уровня
        await state.clear()
        
        await callback.answer(f"Уровень {level} выбран!")
        logger.info(f"User {user_id} registered with level {level}")
        
    except Exception as e:
        logger.error(f"Error creating user {user_id}: {e}", exc_info=True)
        await callback.answer("❌ Ошибка регистрации. Попробуйте еще раз.")


@router.callback_query(F.data == CallbackData.START_TASKS)
async def process_start_tasks(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка нажатия кнопки "Начать первое задание".
    
    Перенаправляет пользователя на получение первого задания.
    
    Args:
        callback: Callback query
        state: FSM context
    """
    await callback.answer()
    
    # Отправляем сообщение с инструкцией
    instructions_text = (
        f"🎉 Отлично! Начинаем обучение!\n\n"
        f"💡 <b>Чтобы получить задание, используйте команду:</b>\n"
        f"/task\n\n"
        f"📌 <b>Полезные команды:</b>\n"
        f"/task - Получить текущее задание\n"
        f"/progress - Посмотреть свой прогресс\n"
        f"/help - Справка по командам"
    )
    
    await callback.message.answer(instructions_text)
    
    # Сбрасываем состояние
    await state.clear()
    
    logger.info(f"User {callback.from_user.id} started tasks")


@router.callback_query(F.data == CallbackData.CONTINUE_TASKS)
async def process_continue_tasks(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка нажатия кнопки "Продолжить".
    
    Отправляет инструкцию по получению следующего задания.
    
    Args:
        callback: Callback query
        state: FSM context
    """
    await callback.answer()
    
    instructions_text = (
        f"▶️ Продолжаем!\n\n"
        f"💡 Используйте команду <b>/task</b> для получения следующего задания."
    )
    
    await callback.message.answer(instructions_text)
    await state.clear()
    
    logger.info(f"User {callback.from_user.id} continues tasks")

