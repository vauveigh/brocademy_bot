# Theme Management Implementation - Этап 2.4

## Описание

Реализация методов для управления темами и навигации между ними. Включает получение информации о темах, определение следующей темы, подсчет доступных тем и обработку окончания контента.

**Дата создания:** 26 октября 2024  
**Статус:** ✅ Завершено и протестировано

---

## 🔧 Реализованные методы

### 1. `get_theme_info(level, theme_order) -> Optional[Dict]`

Получение детальной информации о теме.

**Статус:** ✅ Реализовано в Этапе 2.2

**Параметры:**
- `level` (str): Уровень сложности (Beginner/Elementary/Advanced)
- `theme_order` (int): Порядковый номер темы

**Возвращает:**
```python
{
    "theme_name": "Family and Friends",
    "theme_order": 1,
    "level": "Beginner",
    "total_tasks": 15
}
```
Или `None` если тема не найдена.

**Пример:**
```python
from database.notion_client import get_notion_client

notion = get_notion_client()
theme_info = notion.get_theme_info("Beginner", 1)

if theme_info:
    print(f"Theme: {theme_info['theme_name']}")
    print(f"Tasks: {theme_info['total_tasks']}")
```

---

### 2. `get_next_theme_order(level, current_theme_order) -> Optional[int]`

Получение номера следующей темы для навигации.

**Параметры:**
- `level` (str): Уровень сложности
- `current_theme_order` (int): Текущий порядковый номер темы

**Возвращает:**
- `int` - номер следующей темы
- `None` - если тем больше нет (контент закончился)

**Логика:**
- Ищет темы с `theme_order > current_theme_order`
- Сортирует по возрастанию
- Возвращает первую найденную
- Учитывает только активные темы (`status = "active"`)

**Пример:**
```python
notion = get_notion_client()

# Текущая тема - 1
next_theme = notion.get_next_theme_order("Beginner", 1)

if next_theme:
    print(f"Next theme: {next_theme}")
    # Переходим к следующей теме
    db.update_user_progress(user_id, theme_order=next_theme)
else:
    print("All themes completed!")
    # Поздравляем пользователя
```

**Использование в боте:**
```python
# После завершения темы (5 дней, 15 заданий)
user = db.get_user(user_id)
next_theme = notion.get_next_theme_order(user['level'], user['theme_order'])

if next_theme:
    # Переходим к следующей теме
    db.update_user_progress(
        user_id,
        theme_order=next_theme,
        current_day=1,
        task_in_day=1
    )
    
    # Получаем информацию о новой теме
    theme_info = notion.get_theme_info(user['level'], next_theme)
    
    await message.answer(
        f"🎊 Тема завершена!\n\n"
        f"🚀 Завтра начнем новую тему:\n"
        f"📖 {theme_info['theme_name']}\n\n"
        f"Увидимся завтра в 9:00! ⏰"
    )
else:
    # Все темы пройдены
    await message.answer(
        "🎉 Поздравляем!\n\n"
        "Вы прошли ВСЕ доступные темы! 🏆\n"
        "Это невероятное достижение!\n\n"
        "💪 Ваш уровень значительно вырос!"
    )
```

---

### 3. `get_available_themes_count(level) -> int`

Подсчет количества уникальных тем для уровня.

**Параметры:**
- `level` (str): Уровень сложности

**Возвращает:**
- `int` - количество уникальных тем

**Логика:**
- Получает все активные задания уровня
- Собирает уникальные `theme_order` в set
- Учитывает пагинацию (>100 результатов)
- Возвращает `len(unique_theme_orders)`

**Пример:**
```python
notion = get_notion_client()

# Сколько тем доступно для каждого уровня?
for level in ["Beginner", "Elementary", "Advanced"]:
    count = notion.get_available_themes_count(level)
    print(f"{level}: {count} themes")
```

**Использование:**
```python
# Проверка достаточности контента
beginner_themes = notion.get_available_themes_count("Beginner")

if beginner_themes < 5:
    print(f"⚠️ Warning: Only {beginner_themes} themes for Beginner")
    print("Recommendation: Add more themes to Notion")
```

---

### 4. `get_all_themes_for_level(level) -> List[Dict]`

Получение списка всех тем для уровня (бонусный метод).

**Параметры:**
- `level` (str): Уровень сложности

**Возвращает:**
```python
[
    {
        "theme_name": "Family and Friends",
        "theme_order": 1,
        "level": "Beginner",
        "total_tasks": 15
    },
    {
        "theme_name": "Daily Routine",
        "theme_order": 2,
        "level": "Beginner",
        "total_tasks": 15
    },
    ...
]
```

**Особенности:**
- Собирает информацию о всех темах за один проход
- Автоматически группирует задания по theme_order
- Подсчитывает количество заданий в каждой теме
- Сортирует по theme_order

**Пример:**
```python
notion = get_notion_client()
themes = notion.get_all_themes_for_level("Beginner")

print(f"Available themes for Beginner:")
for theme in themes:
    print(f"  {theme['theme_order']}. {theme['theme_name']} ({theme['total_tasks']} tasks)")
```

**Использование в боте (команда /themes):**
```python
@router.message(Command("themes"))
async def show_themes(message: Message):
    """Показать список всех доступных тем"""
    user = db.get_user(message.from_user.id)
    themes = notion.get_all_themes_for_level(user['level'])
    
    text = f"📚 Доступные темы ({user['level']}):\n\n"
    
    for theme in themes:
        status = "✅" if theme['theme_order'] < user['theme_order'] else "📖"
        current = "👉" if theme['theme_order'] == user['theme_order'] else "  "
        
        text += f"{current}{status} {theme['theme_order']}. {theme['theme_name']}\n"
        text += f"    {theme['total_tasks']} заданий\n\n"
    
    await message.answer(text)
```

---

## 🎯 Обработка окончания контента

### Сценарий: Пользователь прошел все темы

```python
def check_theme_completion(user_id: int, current_theme_order: int):
    """
    Проверка и обработка завершения текущей темы.
    
    Returns:
        bool: True если есть следующая тема, False если контент закончился
    """
    user = db.get_user(user_id)
    
    # Проверяем, есть ли следующая тема
    next_theme = notion.get_next_theme_order(user['level'], current_theme_order)
    
    if next_theme:
        # Есть следующая тема
        db.update_user_progress(
            user_id,
            theme_order=next_theme,
            current_day=1,
            task_in_day=1
        )
        return True
    else:
        # Контент закончился
        # Можем предложить:
        # 1. Повторить темы
        # 2. Перейти на следующий уровень
        # 3. Поздравить и завершить
        return False
```

### Варианты действий при окончании контента

**Вариант 1: Повторение тем**
```python
if not next_theme:
    await message.answer(
        "🎉 Вы прошли все темы!\n\n"
        "Хотите повторить материал?\n"
        "Используйте /restart для повтора с первой темы"
    )
```

**Вариант 2: Переход на следующий уровень**
```python
if not next_theme:
    # Предлагаем перейти на следующий уровень
    current_level = user['level']
    level_progression = {
        "Beginner": "Elementary",
        "Elementary": "Advanced",
        "Advanced": None
    }
    
    next_level = level_progression.get(current_level)
    
    if next_level:
        await message.answer(
            f"🎊 Поздравляем! Вы завершили уровень {current_level}!\n\n"
            f"🚀 Готовы перейти на {next_level}?\n"
            f"Используйте /changelevel"
        )
```

**Вариант 3: Завершение обучения**
```python
if not next_theme:
    # Получаем общую статистику
    stats = db.get_user_stats(user_id)
    
    await message.answer(
        "🏆 НЕВЕРОЯТНО!\n\n"
        f"Вы прошли ВСЕ {themes_count} тем!\n"
        f"Выполнено заданий: {stats['total_completed']}\n"
        f"Точность: {stats['accuracy']}%\n\n"
        "💪 Ваш английский значительно улучшился!\n"
        "🎓 Продолжайте практиковаться!"
    )
```

---

## 🧪 Тестирование

### Запуск тестов

```bash
python -m database.test_themes
```

### Что тестируется

1. ✅ **Получение информации о теме**
   - get_theme_info() для первой темы
   - Проверка всех полей (name, order, level, total_tasks)

2. ✅ **Получение следующей темы**
   - get_next_theme_order() после первой темы
   - Обработка случая, когда тем больше нет

3. ✅ **Подсчет доступных тем**
   - get_available_themes_count() для уровня
   - Проверка корректности подсчета

4. ✅ **Получение всех тем**
   - get_all_themes_for_level()
   - Проверка структуры данных
   - Проверка сортировки

5. ✅ **Обработка окончания тем**
   - Возврат None после последней темы
   - Корректная обработка несуществующих тем

6. ✅ **Симуляция прогрессии**
   - Прохождение всех тем от первой до последней
   - Проверка логики перехода

7. ✅ **Тестирование для всех уровней**
   - Подсчет тем для каждого доступного уровня

### Результаты тестирования

```
✅ ALL TESTS PASSED!

📝 Summary:
   • Theme management: ✅ Working
   • get_theme_info(): ✅ Working
   • get_next_theme_order(): ✅ Working
   • get_available_themes_count(): ✅ Working
   • get_all_themes_for_level(): ✅ Working
   • End of themes handling: ✅ Working

📊 Results:
   • Test level: Beginner
   • Total themes: 1
   • Theme progression: 1 themes
```

---

## 📊 Примеры использования

### Базовая навигация между темами

```python
from database.notion_client import get_notion_client
from database.db_manager import DatabaseManager

db = DatabaseManager()
notion = get_notion_client()

user = db.get_user(user_id)

# Текущая тема
current_theme_info = notion.get_theme_info(
    user['level'],
    user['theme_order']
)
print(f"Current: {current_theme_info['theme_name']}")

# Следующая тема
next_order = notion.get_next_theme_order(
    user['level'],
    user['theme_order']
)

if next_order:
    next_theme_info = notion.get_theme_info(user['level'], next_order)
    print(f"Next: {next_theme_info['theme_name']}")
else:
    print("No more themes!")
```

### Прогресс-бар тем

```python
def get_theme_progress(user_id: int) -> str:
    """Получить прогресс-бар по темам"""
    user = db.get_user(user_id)
    total_themes = notion.get_available_themes_count(user['level'])
    current = user['theme_order']
    
    # Прогресс
    percent = int((current / total_themes) * 100)
    completed = "█" * (percent // 10)
    remaining = "░" * (10 - (percent // 10))
    
    return (
        f"📊 Прогресс: {current}/{total_themes} тем\n"
        f"[{completed}{remaining}] {percent}%"
    )
```

### Статистика по темам

```python
def get_theme_statistics(level: str):
    """Статистика по всем темам уровня"""
    themes = notion.get_all_themes_for_level(level)
    
    total_tasks = sum(t['total_tasks'] for t in themes)
    avg_tasks = total_tasks / len(themes) if themes else 0
    
    print(f"Level: {level}")
    print(f"Total themes: {len(themes)}")
    print(f"Total tasks: {total_tasks}")
    print(f"Average tasks per theme: {avg_tasks:.1f}")
    
    return {
        'themes_count': len(themes),
        'total_tasks': total_tasks,
        'average_tasks': avg_tasks
    }
```

---

## 🔄 Циклическое прохождение (опционально)

Если нужно, чтобы пользователь мог повторно проходить темы:

```python
def handle_theme_completion(user_id: int) -> bool:
    """
    Обработка завершения темы с возможностью зацикливания.
    
    Returns:
        bool: True если установлена следующая тема
    """
    user = db.get_user(user_id)
    next_theme = notion.get_next_theme_order(user['level'], user['theme_order'])
    
    if next_theme:
        # Есть следующая тема
        db.update_user_progress(user_id, theme_order=next_theme)
        return True
    else:
        # Контент закончился - начинаем сначала
        db.update_user_progress(
            user_id,
            theme_order=1,  # Возврат к первой теме
            current_day=1,
            task_in_day=1
        )
        
        # Уведомляем пользователя
        await message.answer(
            "🎊 Все темы пройдены!\n\n"
            "🔄 Начинаем повторный цикл с первой темы.\n"
            "Повторение - мать учения! 📚"
        )
        return True
```

---

## ✅ Завершено

- [X] Реализован `get_theme_info()` (Этап 2.2)
- [X] Реализован `get_next_theme_order()`
- [X] Реализован `get_available_themes_count()`
- [X] Реализован `get_all_themes_for_level()` (бонус)
- [X] Обработка случая окончания тем (возврат None)
- [X] Создан тестовый скрипт `test_themes.py`
- [X] Протестировано получение информации о темах
- [X] Протестирована навигация между темами
- [X] Протестирована симуляция прогрессии
- [X] Создана документация

---

## 🚀 Интеграция с ботом

Эти методы готовы к использованию в Telegram боте:

```python
# В обработчике завершения темы
from database.notion_client import get_notion_client
from database.db_manager import DatabaseManager

db = DatabaseManager()
notion = get_notion_client()

# После того как пользователь прошел 5 дней (15 заданий)
user = db.get_user(user_id)
next_theme = notion.get_next_theme_order(user['level'], user['theme_order'])

if next_theme:
    # Переходим к следующей теме
    db.update_user_progress(
        user_id,
        theme_order=next_theme,
        current_day=1,
        task_in_day=1
    )
    
    # Получаем название новой темы
    theme_info = notion.get_theme_info(user['level'], next_theme)
    
    await message.answer(
        f"🎊 Тема '{user['current_theme']}' завершена!\n\n"
        f"📊 Статистика темы:\n"
        f"   • Выполнено: 15/15 заданий\n"
        f"   • Точность: {theme_accuracy}%\n\n"
        f"🚀 Завтра начнем новую тему:\n"
        f"   📖 {theme_info['theme_name']}\n\n"
        f"Увидимся завтра в 9:00! ⏰"
    )
else:
    # Все темы пройдены!
    total_themes = notion.get_available_themes_count(user['level'])
    
    await message.answer(
        f"🏆 ПОЗДРАВЛЯЕМ!\n\n"
        f"Вы прошли ВСЕ {total_themes} тем уровня {user['level']}!\n\n"
        f"💪 Это невероятное достижение!\n"
        f"🎓 Ваш английский значительно улучшился!\n\n"
        f"Хотите перейти на следующий уровень?\n"
        f"Используйте /changelevel"
    )
```

---

**Дата завершения:** 26 октября 2024  
**Следующий этап:** 3 - Telegram Bot (базовый функционал)


