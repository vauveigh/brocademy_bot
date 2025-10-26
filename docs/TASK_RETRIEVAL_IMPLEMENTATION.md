# Task Retrieval Implementation - Этап 2.2

## Описание

Реализация методов для получения заданий из Notion и парсинга всех полей. Включает получение конкретных заданий, информации о темах, и обработку вариантов ответов.

**Дата создания:** 26 октября 2024  
**Статус:** ✅ Завершено и протестировано

---

## 📁 Добавленная функциональность

### 1. Класс `Task` (dataclass)

Представление задания с полной информацией и вспомогательными методами.

```python
@dataclass
class Task:
    task_id: str
    theme: str
    theme_order: int
    level: str
    task_type: str
    day: int
    task_number: int
    question: str
    answer_type: str
    answer_options: List[str]
    correct_answer: str
    explanation: Optional[str]
    media_url: Optional[str]
    media_type: str
    status: str
    notion_page_id: str
```

**Методы:**
- `has_media()` - проверка наличия медиафайла
- `is_multiple_choice()` - проверка типа задания (выбор ответа)
- `is_open_question()` - проверка типа задания (открытый вопрос)
- `has_explanation()` - проверка наличия объяснения
- `__str__()` - строковое представление

---

## 🔧 Реализованные методы

### 1. `get_task(level, theme_order, day, task_number) -> Optional[Task]`

Получение конкретного задания из Notion по параметрам.

**Параметры:**
- `level` (str): Уровень сложности (Beginner/Elementary/Advanced)
- `theme_order` (int): Порядковый номер темы (1, 2, 3...)
- `day` (int): День цикла (1-5)
- `task_number` (int): Номер задания в дне (1-3)

**Возвращает:**
- `Task` - объект задания со всеми полями
- `None` - если задание не найдено

**Пример:**
```python
from database.notion_client import get_notion_client

notion = get_notion_client()
task = notion.get_task("Beginner", 1, 1, 1)

if task:
    print(f"Question: {task.question}")
    print(f"Options: {task.answer_options}")
    print(f"Correct: {task.correct_answer}")
```

**Фильтрация:**
- По уровню (Уровень - Select)
- По порядку темы (Порядок темы - Number)
- По дню цикла (День цикла - Number)
- По номеру задания (Номер в дне - Number)
- Только активные задания (Статус - Select = "active")

**Обработка ошибок:**
- Возвращает `None` если задание не найдено
- Выбрасывает `NotionDataError` при ошибке API

---

### 2. `get_theme_info(level, theme_order) -> Optional[Dict]`

Получение информации о теме.

**Параметры:**
- `level` (str): Уровень сложности
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

**Пример:**
```python
theme_info = notion.get_theme_info("Beginner", 1)
print(f"Theme: {theme_info['theme_name']}")
print(f"Total tasks: {theme_info['total_tasks']}")
```

---

### 3. `_parse_task(page) -> Task`

Внутренний метод для парсинга страницы Notion в объект Task.

**Парсит следующие поля:**

| Notion Field | Python Type | Notion Type | Method |
|--------------|-------------|-------------|--------|
| ID задания | str | Title | `_extract_title()` |
| Тема | str | Select | `_extract_select()` |
| Порядок темы | int | Number | `_extract_number()` |
| Уровень | str | Select | `_extract_select()` |
| Тип задания | str | Select | `_extract_select()` |
| День цикла | int | Number | `_extract_number()` |
| Номер в дне | int | Number | `_extract_number()` |
| Вопрос | str | Rich Text | `_extract_rich_text()` |
| Тип ответа | str | Select | `_extract_select()` |
| Варианты ответов | List[str] | Rich Text | `_extract_rich_text()` + split |
| Правильный ответ | str | Rich Text | `_extract_rich_text()` |
| Объяснение | Optional[str] | Rich Text | `_extract_rich_text()` |
| URL медиа | Optional[str] | URL | `_extract_url()` |
| Тип медиа | str | Select | `_extract_select()` |
| Статус | str | Select | `_extract_select()` |

**Обработка вариантов ответов:**
- Поле "Варианты ответов" содержит строку с разделителем `|`
- Пример: `"my | mine | me | I"`
- Парсится в список: `["my", "mine", "me", "I"]`
- Пробелы удаляются автоматически (`.strip()`)

```python
# В Notion: "my | mine | me | I"
# В Task: ["my", "mine", "me", "I"]
answer_options = [
    option.strip()
    for option in answer_options_raw.split("|")
    if option.strip()
]
```

---

## 🔨 Вспомогательные методы

### `_extract_rich_text(property_data) -> str`

Извлечение текста из Rich Text поля Notion.

**Возвращает:**
- Полный текст или пустую строку `""`

### `_extract_select(property_data) -> str`

Извлечение значения из Select поля Notion.

**Возвращает:**
- Выбранное значение или пустую строку `""`

### `_extract_number(property_data) -> int`

Извлечение числа из Number поля Notion.

**Возвращает:**
- Число или `0`

### `_extract_url(property_data) -> Optional[str]`

Извлечение URL из URL поля Notion.

**Возвращает:**
- URL или `None`

### `_extract_title(title_array) -> str`

Извлечение текста из Title поля Notion (уже существовал).

**Возвращает:**
- Текст или `"Untitled"`

---

## 🧪 Тестирование

### Запуск тестов

```bash
python -m database.test_get_tasks
```

### Что тестируется

1. ✅ **Подключение к Notion**
   - Инициализация клиента
   - Проверка соединения

2. ✅ **Получение метаданных**
   - Список доступных уровней
   - Подсчет заданий по уровням

3. ✅ **Получение информации о теме**
   - Название темы
   - Количество заданий в теме

4. ✅ **Получение конкретного задания**
   - Парсинг всех полей
   - ID, тема, уровень, день, номер

5. ✅ **Парсинг контента**
   - Текст вопроса
   - Тип ответа
   - Варианты ответов (split по `|`)
   - Правильный ответ
   - Объяснение (опциональное)

6. ✅ **Работа с медиа**
   - URL медиафайла
   - Тип медиа
   - Метод `has_media()`

7. ✅ **Методы класса Task**
   - `is_multiple_choice()`
   - `is_open_question()`
   - `has_explanation()`
   - `has_media()`
   - `__str__()`

8. ✅ **Получение разных заданий**
   - День 1, Задание 2
   - День 2, Задание 1
   - День 3, Задание 1

9. ✅ **Обработка несуществующих заданий**
   - Возврат `None` для несуществующего theme_order

### Результаты тестирования

```
✅ ALL TESTS PASSED!

📝 Summary:
   • Database connection: ✅ Working
   • Total tasks: 15
   • Theme info retrieval: ✅ Working
   • Task retrieval: ✅ Working
   • Task parsing: ✅ All fields parsed correctly
   • Answer options split: ✅ Working
   • Task methods: ✅ All methods working

🚀 Stage 2.2 implementation is ready!
```

---

## 📊 Примеры использования

### Базовое получение задания

```python
from database.notion_client import get_notion_client

# Получаем клиента
notion = get_notion_client()

# Получаем задание: Beginner, Тема 1, День 1, Задание 1
task = notion.get_task("Beginner", 1, 1, 1)

if task:
    print(f"📝 {task.task_id}")
    print(f"❓ {task.question}")
    print(f"✅ {task.correct_answer}")
```

### Работа с multiple choice

```python
task = notion.get_task("Beginner", 1, 1, 1)

if task and task.is_multiple_choice():
    print(f"Question: {task.question}")
    print("Options:")
    for i, option in enumerate(task.answer_options, 1):
        emoji = "✅" if option == task.correct_answer else "⚪"
        print(f"  {emoji} {i}. {option}")
```

### Проверка ответа пользователя

```python
task = notion.get_task("Beginner", 1, 1, 1)
user_answer = "my"

is_correct = (user_answer == task.correct_answer)

if is_correct:
    print("✅ Правильно!")
    if task.has_explanation():
        print(f"💡 {task.explanation}")
else:
    print(f"❌ Неправильно. Правильный ответ: {task.correct_answer}")
```

### Получение полной темы

```python
# Получаем информацию о теме
theme_info = notion.get_theme_info("Beginner", 1)
print(f"Theme: {theme_info['theme_name']}")
print(f"Total tasks: {theme_info['total_tasks']}")

# Получаем все задания первого дня
print("\n📅 Day 1 tasks:")
for task_num in range(1, 4):  # 1, 2, 3
    task = notion.get_task("Beginner", 1, 1, task_num)
    if task:
        print(f"  #{task_num}: {task.question[:50]}...")
```

### Обработка медиа

```python
task = notion.get_task("Beginner", 1, 2, 1)

if task and task.has_media():
    print(f"Media type: {task.media_type}")
    print(f"Media URL: {task.media_url}")
    
    # В боте:
    if task.media_type == "image":
        await bot.send_photo(chat_id, photo=task.media_url)
    elif task.media_type == "audio":
        await bot.send_audio(chat_id, audio=task.media_url)
    elif task.media_type == "video":
        await bot.send_video(chat_id, video=task.media_url)
```

---

## 🔧 Исправления

### Fix: Типы полей в Notion (26.10.2024)

**Проблема:** Ошибка при фильтрации - "database property number does not match filter select"

**Причина:** Поля "День цикла" и "Номер в дне" в Notion имеют тип Number, а не Select

**Решение:** Изменена фильтрация с `select` на `number`

**Было:**
```python
{"property": "День цикла", "select": {"equals": str(day)}}
{"property": "Номер в дне", "select": {"equals": str(task_number)}}
```

**Стало:**
```python
{"property": "День цикла", "number": {"equals": day}}
{"property": "Номер в дне", "number": {"equals": task_number}}
```

**Также обновлен парсинг:**
```python
# Было
day = int(self._extract_select(properties.get("День цикла", {})))
task_number = int(self._extract_select(properties.get("Номер в дне", {})))

# Стало
day = self._extract_number(properties.get("День цикла", {}))
task_number = self._extract_number(properties.get("Номер в дне", {}))
```

---

## ✅ Завершено

- [X] Создан класс Task (dataclass)
- [X] Реализован метод `get_task()`
- [X] Реализован метод `get_theme_info()`
- [X] Реализован метод `_parse_task()`
- [X] Добавлены вспомогательные методы парсинга
- [X] Реализована обработка вариантов ответов (split по `|`)
- [X] Добавлены методы проверки в класс Task
- [X] Создан тестовый скрипт `test_get_tasks.py`
- [X] Обновлен основной тестовый скрипт
- [X] Протестировано получение разных типов заданий
- [X] Создана документация

---

## 🚀 Интеграция с ботом

Эти методы готовы к использованию в Telegram боте (Этап 3):

```python
# В обработчике команды /task
from database.notion_client import get_notion_client
from database.db_manager import DatabaseManager

db = DatabaseManager()
notion = get_notion_client()

# Получаем прогресс пользователя
user = db.get_user(user_id)

# Получаем задание
task = notion.get_task(
    level=user['level'],
    theme_order=user['theme_order'],
    day=user['current_day'],
    task_number=user['task_in_day']
)

if task:
    # Отправляем задание пользователю
    if task.is_multiple_choice():
        # Создаем inline клавиатуру с вариантами
        keyboard = create_answer_keyboard(task.answer_options)
        await message.answer(task.question, reply_markup=keyboard)
    else:
        # Открытый вопрос
        await message.answer(task.question)
        await message.answer("💬 Напишите ваш ответ:")
```

---

**Дата завершения:** 26 октября 2024  
**Следующий этап:** 2.3 - Работа с медиа / 2.4 - Дополнительные методы для тем


