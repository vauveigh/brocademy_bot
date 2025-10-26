# User Flow - Логика взаимодействия с учеником

## Описание

Этот документ описывает полный flow взаимодействия ученика с ботом от регистрации до завершения темы.

**Дата создания:** 26 октября 2024  
**Статус:** Утверждено для реализации

---

## 🎯 Ключевые принципы UX

1. **Простота**: Минимум команд и кнопок
2. **Автоматизация**: Бот сам ведет пользователя по заданиям
3. **Ограничение**: 3 задания в день = дневной лимит
4. **Предсказуемость**: Четкое расписание и напоминания
5. **Мотивация**: Статистика, поддержка, прогресс

---

## 📅 Правило дневного лимита

### **3 задания в день = автоматическая остановка**

```
День 1: Задание 1 → Задание 2 → Задание 3 → СТОП
                                              ↓
                                    "День завершен!
                                     Увидимся завтра в 9:00"
```

**Логика:**
- После выполнения 3-го задания бот **автоматически** завершает день
- Пользователь **не может** выполнить больше 3 заданий за день
- При попытке `/task` после лимита: "Уже выполнил все задания на сегодня"
- Следующие задания доступны только на следующий день

---

## 🔄 Полный Flow пользователя

### 1️⃣ **Первый запуск: Регистрация**

```
ПОЛЬЗОВАТЕЛЬ → /start
    ↓
БОТ: Приветственное сообщение
    👋 Привет! Я помогу тебе практиковать английский каждый день.
    
    📚 Как это работает:
    • Каждый день 3 коротких задания (5-10 минут)
    • 5 дней = 1 тема (15 заданий)
    • Задания приходят каждый день в 9:00
    
    Выбери свой уровень:
    
    [Beginner] [Elementary] [Advanced]
    ↓
ПОЛЬЗОВАТЕЛЬ → нажимает кнопку уровня
    ↓
БОТ: Вызывает create_user(user_id, username, level)
    → Создается запись в БД:
       - level = выбранный уровень
       - current_day = 1
       - theme_order = 1
       - task_in_day = 1
       - current_theme = NULL
    ↓
БОТ: Подтверждение
    ✅ Отлично! Ты начинаешь с уровня {level}.
    
    🎯 Твоя первая тема: "Family and Friends"
    📅 Каждый день тебе будет приходить 3 задания.
    
    Готов начать? 👇
    
    [🚀 Начать первое задание!]
```

**Технические детали:**
- FSM state: `idle` → `registered`
- БД: `create_user(user_id, username, level)`
- Кэш: Предзагрузка первой темы из Notion (опционально)

---

### 2️⃣ **Получение первого задания**

```
ПОЛЬЗОВАТЕЛЬ → нажимает "Начать" или /task
    ↓
БОТ: Проверка состояния
    1. user = get_user(user_id)
    2. progress = get_current_day_progress(user_id)
    3. Проверка: completed_today < 3 ?
    ↓
БОТ: Загрузка задания из Notion
    notion.get_task(
        level = user['level'],
        theme_order = user['theme_order'],
        day = user['current_day'],
        task_number = user['task_in_day']
    )
    ↓
БОТ: Отправка задания
    📚 Тема: Family and Friends
    📅 День 1/5: Grammar
    🎯 Задание 1/3
    
    ❓ Complete the sentence:
    'This is ___ mother.'
    
    [my] [me] [I] [mine]  ← Inline keyboard для multiple choice
    
    ИЛИ
    
    💬 Напишите ваш ответ:  ← Для open question
```

**Технические детали:**
- FSM state: `waiting_for_answer`
- Сохранение текущего задания в state: `current_task`
- Определение типа задания по дню (day 1 = grammar)

---

### 3️⃣ **Ответ на задание (Multiple Choice)**

```
ПОЛЬЗОВАТЕЛЬ → нажимает кнопку ответа
    ↓
БОТ: Проверка ответа
    is_correct = (selected_answer == task['correct_answer'])
    ↓
БОТ: Сохранение в БД
    save_task_answer(
        user_id,
        task_id,
        task_type,
        answer,
        is_correct
    )
    ↓
БОТ: Обратная связь
    
    ЕСЛИ правильно:
        ✅ Правильно! Отлично!
        
        💡 Explanation: 'My' is a possessive adjective 
        used before a noun to show ownership.
    
    ЕСЛИ неправильно:
        ❌ Неправильно.
        
        Правильный ответ: my
        
        💡 Explanation: 'My' is a possessive adjective...
    ↓
БОТ: Переход к следующему
    result = advance_to_next_task(user_id)
    ↓
БОТ: Определение действия
    
    ЕСЛИ task_in_day < 3:
        → АВТОМАТИЧЕСКИ отправить следующее задание
        [пауза 1 секунда]
        📚 Тема: Family and Friends
        📅 День 1/5: Grammar
        🎯 Задание 2/3
        ...
    
    ЕСЛИ task_in_day = 3 И current_day < 5:
        → День завершен
        🎉 День завершен! Отличная работа!
        
        📊 Сегодня: 3/3 задания
        💯 Точность: 67%
        
        🎯 Завтра: День 2/5 - Reading
        
        🌙 Увидимся завтра! Напишу в 9:00 ⏰
    
    ЕСЛИ task_in_day = 3 И current_day = 5:
        → Тема завершена
        🎊 ТЕМА ЗАВЕРШЕНА! 🎊
        
        🏆 Тема: "Family and Friends"
        
        📊 Итоговая статистика:
           • Выполнено: 15 заданий за 5 дней
           • Общая точность: 87%
           • Лучший день: День 2 (100%) 🌟
        
        🎯 По типам заданий:
           - Grammar: 67%
           - Reading: 100% 🌟
           - Vocabulary: 100% 🌟
           - Situations: 67%
           - Review: ⏳ (ждет проверки)
        
        🚀 Завтра начнем новую тему!
           Тема #2: "Daily Routine"
        
        🔔 Напишу завтра в 9:00!
        
        Отличная работа! 💪
```

**Технические детали:**
- Callback handler для inline buttons: `@router.callback_query(F.data.startswith("answer:"))`
- Извлечение ответа: `answer = callback.data.split(":")[1]`
- Автоматическая отправка через `asyncio.sleep(1)` для плавности

---

### 4️⃣ **Ответ на открытый вопрос**

```
[Обычно на День 5 - Review]

БОТ: Отправка открытого вопроса
    📚 Тема: Family and Friends
    📅 День 5/5: Review
    🎯 Задание 3/3
    
    ❓ Describe your family in 3-4 sentences.
    
    💬 Напишите ваш ответ:
    ↓
ПОЛЬЗОВАТЕЛЬ → пишет текстовый ответ
    "My family is small. I have a mother, father and sister.
     We live in Moscow. We are very happy."
    ↓
БОТ: Сохранение ответа
    save_open_answer(
        user_id,
        task_id,
        question,
        user_answer
    )
    
    save_task_answer(
        user_id,
        task_id,
        task_type,
        user_answer,
        is_correct=None  # Ожидает проверки
    )
    ↓
БОТ: Подтверждение
    ✅ Ваш ответ принят!
    
    📝 Ответ будет проверен преподавателем.
    ⏳ Вы получите уведомление после проверки.
    ↓
БОТ: Переход к следующей теме (если это было последнее задание)
    [Показывается статистика темы и "увидимся завтра"]
```

**Технические детали:**
- FSM state: `waiting_for_text_answer`
- Message handler: `@router.message(F.text, StateFilter(TaskStates.waiting_for_answer))`
- Сохранение в обе таблицы: `user_answers` и `user_progress`

---

### 5️⃣ **Утреннее напоминание (автоматическое)**

```
[Каждый день в 9:00]

БОТ → ПОЛЬЗОВАТЕЛЮ:
    🌅 Доброе утро!
    
    📚 Тема: Family and Friends
    📅 Сегодня: День 2/5 - Reading
    🎯 Тебя ждут 3 задания!
    
    Начнем? 👇
    
    [🚀 Начать!]
```

**Технические детали:**
- APScheduler: `@scheduler.scheduled_job('cron', hour=9, minute=0)`
- Проверка: `if progress['completed_today'] == 0`
- Персонализация: текущий день, тема, тип заданий

---

### 6️⃣ **Попытка выполнить больше 3 заданий**

```
[Пользователь уже выполнил 3 задания]

ПОЛЬЗОВАТЕЛЬ → /task
    ↓
БОТ: Проверка лимита
    progress = get_current_day_progress(user_id)
    if progress['completed_today'] >= 3:
        ↓
БОТ: Сообщение об ограничении
    ⚠️ Ты уже выполнил все задания на сегодня! (3/3)
    
    📊 Сегодняшние результаты:
       • Точность: 100%
       • Время: 8 минут
    
    🎯 Следующие задания: завтра, день 3/5
    
    💡 А пока можешь:
       • Посмотреть статистику: /progress
       • Проверить открытые ответы: /my_answers
       • Повторить материал темы
    
    Увидимся завтра! ⏰
```

---

## 🎮 Дополнительные команды

### `/progress` - Мой прогресс

```
ПОЛЬЗОВАТЕЛЬ → /progress
    ↓
БОТ: Детальная статистика
    📊 Ваш прогресс:
    
    📍 Текущая позиция:
       • Тема: Family and Friends
       • День: 2/5
       • Задание: 1/3
    
    📈 Сегодня:
       • Выполнено: 0/3
       • Осталось: 3
    
    ✅ Всего выполнено:
       • Заданий: 18
       • Правильно: 15
       • Точность: 83%
    
    📚 По типам заданий:
       📝 Grammar: 67% (2/3)
       📖 Reading: 100% (3/3)
       💭 Vocabulary: 100% (3/3)
       🗣️ Situations: 67% (2/3)
       🔄 Review: ⏳ (ждет проверки)
```

### `/my_answers` - Мои открытые ответы

```
ПОЛЬЗОВАТЕЛЬ → /my_answers
    ↓
БОТ: Список ответов
    📝 Ваши открытые ответы:
    
    ⏳ Ожидают проверки: 2
    
    1. Day 5, Theme: Family and Friends
       Q: Describe your family...
       A: My family is small...
       📅 25.10.2024
    
    2. Day 5, Theme: Daily Routine
       Q: What do you do in the morning?
       A: I wake up at 7...
       📅 26.10.2024
    
    ✅ Проверено: 3
```

### `/help` - Помощь

```
ПОЛЬЗОВАТЕЛЬ → /help
    ↓
БОТ: Список команд и помощь
    ❓ Помощь
    
    📚 Основные команды:
    /task - Получить задание
    /progress - Мой прогресс
    /my_answers - Мои открытые ответы
    /changelevel - Сменить уровень
    /help - Эта справка
    
    💡 Как это работает:
    • Каждый день в 9:00 бот присылает напоминание
    • Ровно 3 задания в день
    • 5 дней = 1 тема
    • После 3-го задания день завершается автоматически
    
    ❓ Есть вопросы? Напиши @support
```

### `/changelevel` - Сменить уровень

```
ПОЛЬЗОВАТЕЛЬ → /changelevel
    ↓
БОТ: Предупреждение
    ⚠️ Смена уровня сбросит ваш текущий прогресс!
    
    Текущий уровень: Beginner
    Прогресс: День 2/5, Тема "Family and Friends"
    
    Вы уверены?
    
    [✅ Да, сменить] [❌ Отмена]
    ↓
ПОЛЬЗОВАТЕЛЬ → подтверждает
    ↓
БОТ: Выбор нового уровня
    Выберите новый уровень:
    
    [Beginner] [Elementary] [Advanced]
    ↓
ПОЛЬЗОВАТЕЛЬ → выбирает
    ↓
БОТ: Обновление
    update_user_level(user_id, new_level)
    
    ✅ Уровень изменен на Elementary!
    
    🔄 Прогресс сброшен.
    Начинаем с темы #1.
    
    Готовы начать? /task
```

---

## 🔄 Автоматические переходы

### Логика `advance_to_next_task()`

```python
# После каждого ответа
result = advance_to_next_task(user_id)

# result['transition_type'] может быть:
# - "next_task" → следующее задание в текущем дне
# - "next_day" → следующий день
# - "next_theme" → новая тема

# Действия бота:
if result['transition_type'] == 'next_task':
    # АВТОМАТИЧЕСКИ отправить следующее задание
    await send_next_task(message, user_id)

elif result['transition_type'] == 'next_day':
    # Показать статистику + "увидимся завтра"
    await message.answer(day_completion_message)

elif result['transition_type'] == 'next_theme':
    # Показать итоговую статистику темы + "завтра новая тема"
    await message.answer(theme_completion_message)
```

### Таблица переходов

| Текущее состояние | Действие | Новое состояние | Сообщение бота |
|-------------------|----------|-----------------|----------------|
| День 1, Задание 1 | Ответ | День 1, Задание 2 | "Правильно!" + автоматически задание 2 |
| День 1, Задание 2 | Ответ | День 1, Задание 3 | "Правильно!" + автоматически задание 3 |
| День 1, Задание 3 | Ответ | День 2, Задание 1 | "День завершен! Увидимся завтра" |
| День 2-4, Задание 3 | Ответ | День N+1, Задание 1 | "День завершен! Увидимся завтра" |
| День 5, Задание 3 | Ответ | День 1, Задание 1 (новая тема) | "Тема завершена! Завтра новая тема" |

---

## ⏰ Расписание и напоминания

### Ежедневные напоминания (9:00)

```python
@scheduler.scheduled_job('cron', hour=9, minute=0)
async def morning_reminder():
    """Отправить утренние напоминания всем пользователям"""
    
    users = get_all_active_users()
    
    for user in users:
        progress = get_current_day_progress(user['user_id'])
        
        # Если еще не выполнил задания сегодня
        if progress['completed_today'] == 0:
            day_name = get_day_name(progress['current_day'])
            
            await bot.send_message(
                user['user_id'],
                f"🌅 Доброе утро!\n\n"
                f"📚 Тема: {progress['current_theme']}\n"
                f"📅 Сегодня: День {progress['current_day']}/5 - {day_name}\n"
                f"🎯 Тебя ждут 3 задания!\n\n"
                f"Начнем? 👇",
                reply_markup=start_button_keyboard
            )
```

### Названия дней

```python
def get_day_name(day: int) -> str:
    """Получить название дня по номеру"""
    day_names = {
        1: "Grammar",
        2: "Reading",
        3: "Vocabulary",
        4: "Situations",
        5: "Review"
    }
    return day_names.get(day, "Unknown")
```

---

## 📊 Статистика и мотивация

### После каждого дня
- Точность за день
- Количество правильных/неправильных
- Мотивационное сообщение

### После каждой темы
- Итоговая точность по теме
- Разбивка по типам заданий
- Лучший день
- Поздравление

### В /progress
- Текущая позиция
- Сегодняшний прогресс
- Общая статистика
- Точность по типам заданий

---

## 🎯 FSM States (Состояния)

```python
class TaskStates(StatesGroup):
    idle = State()                      # Ожидание команды
    waiting_for_answer = State()        # Ожидание ответа на задание
    waiting_for_level_change = State()  # Подтверждение смены уровня
```

---

## 🔍 Проверка дневного лимита

```python
def can_get_task(user_id: int) -> tuple[bool, str]:
    """
    Проверить, может ли пользователь получить задание.
    
    Returns:
        (can_continue, message)
    """
    progress = get_current_day_progress(user_id)
    
    if progress['completed_today'] >= 3:
        return (
            False,
            f"⚠️ Ты уже выполнил все задания на сегодня! ({progress['completed_today']}/3)\n\n"
            f"🎯 Следующие задания: завтра\n"
            f"🔔 Напишу в 9:00 ⏰"
        )
    
    return (True, None)
```

---

## 📱 Inline клавиатуры

### Кнопка "Начать задания"

```python
start_button = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="🚀 Начать!", callback_data="start_day")
]])
```

### Варианты ответов (Multiple Choice)

```python
def create_answer_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    """Создать клавиатуру с вариантами ответа"""
    buttons = [
        [InlineKeyboardButton(text=option, callback_data=f"answer:{option}")]
        for option in options
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
```

### Выбор уровня

```python
level_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Beginner", callback_data="level:Beginner")],
    [InlineKeyboardButton(text="Elementary", callback_data="level:Elementary")],
    [InlineKeyboardButton(text="Advanced", callback_data="level:Advanced")]
])
```

---

## ✅ Чек-лист для реализации

- [ ] FSM настроен с правильными states
- [ ] Команда /start с выбором уровня
- [ ] Команда /task с проверкой дневного лимита
- [ ] Обработка ответов (inline buttons + текст)
- [ ] Автоматическая отправка следующего задания
- [ ] Автоматическая остановка после 3 заданий
- [ ] Сообщения о завершении дня
- [ ] Сообщения о завершении темы
- [ ] Утренние напоминания (APScheduler)
- [ ] Команда /progress
- [ ] Команда /my_answers
- [ ] Команда /changelevel
- [ ] Обработка ошибок (задание не найдено, Notion недоступен)
- [ ] Логирование всех действий

---

## 🚀 Готовность к реализации

Этот документ описывает полный UX и служит **спецификацией** для разработки Telegram бота (Этап 3).

**Связанные документы:**
- [roadmap.md](roadmap.md) - План разработки
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Схема БД
- [NOTION_DB_STRUCTURE.md](NOTION_DB_STRUCTURE.md) - Структура Notion

**Дата последнего обновления:** 26 октября 2024

