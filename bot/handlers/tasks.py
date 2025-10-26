"""
Tasks Handler

Обработчик заданий: получение заданий, обработка ответов (multiple choice и open questions).

Author: Vladimir
Date: 2024-10-26
"""

import logging
import asyncio
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config.config import config
from database.db_manager import DatabaseManager
from database.notion_client import get_notion_client, Task
from bot.states import UserStates, CallbackData, get_answer_from_callback
from bot.keyboards import get_answer_options_keyboard, remove_keyboard
from bot.utils import (
    format_task_message,
    format_day_completion_message,
    format_theme_completion_message,
    get_day_name
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("task"))
async def cmd_task(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /task - получение текущего задания.
    
    Проверяет:
    - Зарегистрирован ли пользователь
    - Не превышен ли дневной лимит (3 задания)
    - Есть ли задание в Notion
    
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
    
    # Проверяем дневной лимит
    progress = db.get_current_day_progress(user_id)
    
    if progress and progress['completed_today'] >= 3:
        # Лимит достигнут
        await message.answer(
            "✅ <b>Отлично! Вы уже выполнили все задания на сегодня!</b>\n\n"
            f"📊 Выполнено: {progress['completed_today']}/3\n"
            f"🌙 Увидимся завтра! Напишу в 9:00 ⏰\n\n"
            f"💡 Вы можете:\n"
            f"• Посмотреть прогресс: /progress\n"
            f"• Проверить свои ответы: /my_answers"
        )
        return
    
    # Получаем задание
    await send_current_task(message, state, user, db)


async def send_current_task(
    message: Message,
    state: FSMContext,
    user: dict,
    db: DatabaseManager
) -> None:
    """
    Отправить текущее задание пользователю.
    
    Args:
        message: Сообщение для ответа
        state: FSM context
        user: Данные пользователя
        db: Database manager
    """
    user_id = user['user_id']
    level = user['level']
    theme_order = user['theme_order']
    current_day = user['current_day']
    task_in_day = user['task_in_day']
    
    # Получаем задание из Notion
    notion = get_notion_client()
    
    try:
        task = notion.get_task(level, theme_order, current_day, task_in_day)
        
        if not task:
            # Задание не найдено
            await message.answer(
                "❌ <b>Задание не найдено</b>\n\n"
                f"Уровень: {level}\n"
                f"Тема: {theme_order}\n"
                f"День: {current_day}\n"
                f"Задание: {task_in_day}\n\n"
                "Обратитесь к администратору."
            )
            logger.error(
                f"Task not found: {level}, theme {theme_order}, "
                f"day {current_day}, task {task_in_day}"
            )
            return
        
        # Сохраняем задание в FSM state
        await state.update_data(
            current_task=task,
            task_sent_at=message.date.timestamp()
        )
        
        # Формируем сообщение с заданием
        task_message = format_task_message(
            task.task_id,
            task.theme,
            current_day,
            task_in_day,
            task.question
        )
        
        # Отправляем медиа, если есть
        if task.has_media():
            await send_media(message, task)
        
        # Отправляем вопрос
        if task.is_multiple_choice():
            # Multiple choice - отправляем с клавиатурой
            keyboard = get_answer_options_keyboard(task.answer_options)
            await message.answer(task_message, reply_markup=keyboard)
            await state.set_state(UserStates.waiting_for_answer)
            
        elif task.is_open_question():
            # Open question - запрашиваем текстовый ответ
            task_message += "\n\n✍️ <b>Напишите свой ответ:</b>"
            await message.answer(task_message)
            await state.set_state(UserStates.waiting_for_text_answer)
        
        logger.info(f"Task {task.task_id} sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error getting task for user {user_id}: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при получении задания.\n"
            "Попробуйте еще раз."
        )


async def send_media(message: Message, task: Task) -> None:
    """
    Отправить медиафайл, если он есть у задания.
    
    Args:
        message: Сообщение для ответа
        task: Объект задания с медиа
    """
    if not task.has_media() or not task.media_url:
        return
    
    try:
        if task.media_type == "image":
            await message.answer_photo(
                task.media_url,
                caption="🖼️ Изображение к заданию"
            )
        elif task.media_type == "audio":
            await message.answer_audio(
                task.media_url,
                caption="🔊 Аудио к заданию"
            )
        elif task.media_type == "video":
            await message.answer_video(
                task.media_url,
                caption="🎥 Видео к заданию"
            )
    except Exception as e:
        logger.error(f"Error sending media: {e}")
        await message.answer("⚠️ Не удалось загрузить медиафайл")


@router.callback_query(
    F.data.startswith(CallbackData.ANSWER_PREFIX),
    UserStates.waiting_for_answer
)
async def process_multiple_choice_answer(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Обработка ответа на multiple choice задание.
    
    Args:
        callback: Callback query с ответом
        state: FSM context
    """
    user_id = callback.from_user.id
    user_answer = get_answer_from_callback(callback.data)
    
    # Получаем задание из state
    data = await state.get_data()
    task: Optional[Task] = data.get('current_task')
    
    if not task:
        await callback.answer("❌ Задание не найдено")
        return
    
    # Проверяем правильность ответа
    is_correct = (user_answer == task.correct_answer)
    
    # Сохраняем ответ в БД
    db = DatabaseManager(config.SQLITE_DB_PATH)
    db.save_task_answer(
        user_id,
        task.task_id,
        task.task_type,
        user_answer,
        is_correct
    )
    
    # Убираем кнопки (чтобы нельзя было ответить повторно)
    await callback.message.edit_reply_markup(reply_markup=remove_keyboard())
    
    # Формируем feedback сообщение
    if is_correct:
        feedback = (
            "✅ <b>Правильно! Отлично!</b> 🎉\n\n"
            f"Ваш ответ: <b>{user_answer}</b>"
        )
    else:
        feedback = (
            f"❌ <b>Неправильно</b>\n\n"
            f"Ваш ответ: <b>{user_answer}</b>\n"
            f"Правильный ответ: <b>{task.correct_answer}</b>"
        )
    
    # Добавляем объяснение, если есть
    if task.has_explanation():
        feedback += f"\n\n💡 <b>Объяснение:</b>\n{task.explanation}"
    
    await callback.message.answer(feedback)
    await callback.answer()
    
    # Переходим к следующему заданию
    await advance_to_next(callback.message, state, user_id, db)


@router.message(UserStates.waiting_for_text_answer)
async def process_open_question_answer(message: Message, state: FSMContext) -> None:
    """
    Обработка ответа на открытый вопрос.
    
    Args:
        message: Сообщение с ответом пользователя
        state: FSM context
    """
    user_id = message.from_user.id
    user_answer = message.text
    
    if not user_answer or len(user_answer.strip()) == 0:
        await message.answer("⚠️ Пожалуйста, напишите ответ.")
        return
    
    # Получаем задание из state
    data = await state.get_data()
    task: Optional[Task] = data.get('current_task')
    
    if not task:
        await message.answer("❌ Задание не найдено")
        return
    
    # Сохраняем открытый ответ
    db = DatabaseManager(config.SQLITE_DB_PATH)
    
    # Сохраняем в user_answers для проверки преподавателем
    db.save_open_answer(
        user_id,
        task.task_id,
        task.question,
        user_answer
    )
    
    # Сохраняем в user_progress с is_correct=None
    db.save_task_answer(
        user_id,
        task.task_id,
        task.task_type,
        user_answer,
        is_correct=None  # Будет проверено преподавателем
    )
    
    # Отправляем подтверждение
    feedback = (
        "✅ <b>Ваш ответ принят!</b>\n\n"
        "📝 Ответ будет проверен преподавателем\n"
        "⏳ Вы получите уведомление после проверки"
    )
    
    await message.answer(feedback)
    
    # Переходим к следующему заданию
    await advance_to_next(message, state, user_id, db)


async def advance_to_next(
    message: Message,
    state: FSMContext,
    user_id: int,
    db: DatabaseManager
) -> None:
    """
    Переход к следующему заданию с обработкой переходов между днями и темами.
    
    Args:
        message: Сообщение для ответа
        state: FSM context
        user_id: ID пользователя
        db: Database manager
    """
    # Вызываем логику перехода из БД
    transition = db.advance_to_next_task(user_id)
    
    if not transition:
        await message.answer("❌ Ошибка перехода к следующему заданию")
        return
    
    transition_type = transition['transition_type']
    
    if transition_type == "next_task":
        # Следующее задание в текущем дне
        await asyncio.sleep(1)  # Небольшая пауза
        
        # Автоматически отправляем следующее задание
        user = db.get_user(user_id)
        await send_current_task(message, state, user, db)
        
    elif transition_type == "next_day":
        # Следующий день
        new_day = transition['new_state']['day']
        
        # Получаем статистику за день
        progress_stats = db.get_user_progress_stats(user_id)
        accuracy = progress_stats['accuracy'] if progress_stats else 0.0
        
        completion_msg = format_day_completion_message(
            completed_today=3,
            accuracy=accuracy,
            next_day=new_day
        )
        
        await message.answer(completion_msg)
        await state.clear()
        
    elif transition_type == "next_theme":
        # Новая тема
        user = db.get_user(user_id)
        new_theme_order = transition['new_state']['theme_order']
        
        # Получаем статистику по завершенной теме
        progress_stats = db.get_user_progress_stats(user_id)
        accuracy = progress_stats['accuracy'] if progress_stats else 0.0
        
        # Получаем информацию о следующей теме
        notion = get_notion_client()
        next_theme_info = notion.get_theme_info(user['level'], new_theme_order)
        
        if next_theme_info:
            next_theme_name = next_theme_info['theme_name']
            
            # Обновляем текущую тему в БД
            db.update_user_progress(user_id, current_theme=next_theme_name)
        else:
            next_theme_name = None
        
        completion_msg = format_theme_completion_message(
            theme_name=user['current_theme'],
            total_tasks=15,
            accuracy=accuracy,
            next_theme_name=next_theme_name
        )
        
        await message.answer(completion_msg)
        await state.clear()
    
    logger.info(
        f"User {user_id} transition: {transition_type} - "
        f"{transition['previous_state']} → {transition['new_state']}"
    )

