# Notion Client Implementation - Этап 2.1

## Описание

Реализация клиента для работы с Notion API. Клиент предоставляет методы для подключения, проверки соединения, получения информации о базе данных и подсчета заданий.

**Дата создания:** 26 октября 2024  
**Статус:** ✅ Завершено

---

## 📁 Созданные файлы

### 1. `database/notion_client.py`

Основной модуль с классом `NotionClient` и вспомогательными функциями.

**Размер:** ~650 строк  
**Классы:** 3 (NotionClient, NotionConnectionError, NotionDataError)  
**Методы:** 10 основных методов

---

## 🔧 Реализованная функциональность

### Класс `NotionClient`

#### Инициализация

```python
notion = NotionClient(api_key=None, database_id=None)
```

- Автоматически загружает credentials из `config.py` (или принимает явно)
- Проверяет наличие API key и Database ID
- Инициализирует Notion API client
- Логирует успешную инициализацию

**Raises:**
- `NotionConnectionError` - если отсутствуют credentials

#### Основные методы

##### 1. `test_connection() -> bool`

Проверка подключения к Notion API.

```python
notion = NotionClient()
if notion.test_connection():
    print("Connection successful!")
```

**Возвращает:**
- `True` - если подключение успешно
- `False` - если произошла ошибка

**Обрабатывает ошибки:**
- `unauthorized` - неверный API key
- `object_not_found` - неверный Database ID или нет доступа
- `RequestTimeoutError` - timeout при подключении

##### 2. `get_database_info() -> Dict[str, Any]`

Получение информации о базе данных.

```python
notion = NotionClient()
info = notion.get_database_info()

print(f"Database: {info['title']}")
print(f"Properties: {', '.join(info['properties'])}")
```

**Возвращает:**
```python
{
    "title": "English Learning Tasks",
    "id": "29793ccf-9636-...",
    "created_time": "2024-10-25T...",
    "last_edited_time": "2024-10-26T...",
    "properties": [
        "ID задания",
        "Тема",
        "Порядок темы",
        "Уровень",
        "Тип задания",
        "День цикла",
        "Номер в дне",
        "Вопрос",
        "Тип ответа",
        "Варианты ответов",
        "Правильный ответ",
        "Объяснение",
        "URL медиа",
        "Тип медиа",
        "Статус"
    ]
}
```

**Raises:**
- `NotionConnectionError` - если не удалось получить информацию

##### 3. `get_database_properties() -> Dict[str, Dict[str, Any]]`

Детальная информация о свойствах базы данных.

```python
notion = NotionClient()
props = notion.get_database_properties()

print(f"Уровень type: {props['Уровень']['type']}")
print(f"Options: {props['Уровень']['options']}")
```

**Возвращает:**
```python
{
    "Уровень": {
        "type": "select",
        "id": "...",
        "options": ["Beginner", "Elementary", "Advanced"]
    },
    "Тема": {
        "type": "select",
        "id": "...",
        "options": ["Family and Friends", "Daily Routine", ...]
    },
    "Вопрос": {
        "type": "rich_text",
        "id": "..."
    },
    ...
}
```

**Raises:**
- `NotionConnectionError` - если не удалось получить информацию

##### 4. `count_tasks(level=None, theme=None) -> int`

Подсчет количества заданий с опциональными фильтрами.

```python
notion = NotionClient()

# Все задания
total = notion.count_tasks()

# По уровню
beginner_tasks = notion.count_tasks(level="Beginner")

# По теме
family_tasks = notion.count_tasks(theme="Family and Friends")

# По уровню и теме
specific = notion.count_tasks(level="Beginner", theme="Family and Friends")
```

**Параметры:**
- `level` (Optional[str]) - фильтр по уровню
- `theme` (Optional[str]) - фильтр по теме

**Возвращает:**
- `int` - количество заданий

**Особенности:**
- Автоматически обрабатывает пагинацию (если больше 100 результатов)
- Использует Notion API фильтры для точного подсчета

**Raises:**
- `NotionDataError` - если не удалось выполнить запрос

##### 5. `get_available_levels() -> List[str]`

Получение списка доступных уровней.

```python
notion = NotionClient()
levels = notion.get_available_levels()
# ["Beginner", "Elementary", "Advanced"]
```

**Возвращает:**
- `List[str]` - список уровней

##### 6. `get_available_themes(level=None) -> List[str]`

Получение списка доступных тем.

```python
notion = NotionClient()

# Все темы
all_themes = notion.get_available_themes()

# Темы конкретного уровня (в будущем)
beginner_themes = notion.get_available_themes(level="Beginner")
```

**Параметры:**
- `level` (Optional[str]) - фильтр по уровню (пока не используется)

**Возвращает:**
- `List[str]` - список тем

---

## 🔒 Обработка ошибок

### Custom Exceptions

#### `NotionConnectionError`

Исключение при ошибках подключения к Notion API.

**Используется в:**
- Инициализации клиента
- Получении информации о БД
- Получении свойств БД

#### `NotionDataError`

Исключение при ошибках получения данных из Notion.

**Используется в:**
- Подсчете заданий
- Фильтрации данных
- Query операциях

### Типы ошибок Notion API

| Код ошибки | Описание | Рекомендации |
|------------|----------|--------------|
| `unauthorized` | Неверный API key | Проверьте NOTION_API_KEY в .env |
| `object_not_found` | База данных не найдена | 1. Проверьте NOTION_DATABASE_ID<br>2. Убедитесь, что интеграция имеет доступ |
| `rate_limited` | Превышен лимит запросов | Повторите запрос через несколько секунд |
| `service_unavailable` | Notion API недоступен | Проверьте статус на status.notion.so |

---

## 📊 Логирование

Все операции логируются с использованием стандартной библиотеки `logging`.

**Уровни логирования:**

### INFO ✅
- Успешная инициализация клиента
- Успешное подключение к БД
- Получение информации о БД
- Подсчет заданий

### WARNING ⚠️
- Пустой ответ от Notion API
- Отсутствие ожидаемых свойств

### ERROR ❌
- Ошибки подключения
- Ошибки API
- Неожиданные исключения

**Пример логов:**

```
INFO:database.notion_client:✅ Notion client initialized successfully
INFO:database.notion_client:✅ Successfully connected to Notion database: 'English Learning Tasks'
INFO:database.notion_client:📊 Database info retrieved: 'English Learning Tasks' with 15 properties
INFO:database.notion_client:📋 Retrieved 15 database properties
INFO:database.notion_client:📚 Available levels: Beginner, Elementary, Advanced
INFO:database.notion_client:📖 Found 10 themes
INFO:database.notion_client:📊 Found 15 tasks (level=Beginner, theme=Family and Friends)
```

---

## 🧪 Тестирование

### Запуск тестового скрипта

```bash
python -m database.notion_client
```

### Тесты, выполняемые скриптом

1. ✅ **Инициализация клиента**
   - Создание экземпляра NotionClient
   - Загрузка credentials из config

2. ✅ **Проверка подключения**
   - Выполнение тестового запроса к API
   - Проверка валидности credentials
   - Проверка доступа к БД

3. ✅ **Получение информации о БД**
   - Название базы данных
   - ID, даты создания и редактирования
   - Список всех свойств

4. ✅ **Получение деталей свойств**
   - Типы свойств
   - Опции для Select полей
   - Проверка наличия важных полей

5. ✅ **Получение доступных уровней**
   - Список всех уровней сложности

6. ✅ **Получение доступных тем**
   - Список всех тем

7. ✅ **Подсчет заданий**
   - Общее количество
   - Количество по каждому уровню

### Ожидаемый вывод (при успехе)

```
============================================================
🔍 NOTION CLIENT CONNECTION TEST
============================================================

1️⃣ Initializing Notion client...
   ✅ Client initialized

2️⃣ Testing connection to Notion API...
   ✅ Connection successful!

3️⃣ Retrieving database information...
   📊 Database: English Learning Tasks
   🆔 ID: 29793ccf-9636-80ac-a7fc-000c4c3a1edd
   📅 Created: 2024-10-25T10:00:00.000Z
   ✏️  Last edited: 2024-10-26T12:30:00.000Z
   📋 Properties (15):
      • ID задания
      • Тема
      • Порядок темы
      • Уровень
      • Тип задания
      • День цикла
      • Номер в дне
      • Вопрос
      • Тип ответа
      • Варианты ответов
      • Правильный ответ
      • Объяснение
      • URL медиа
      • Тип медиа
      • Статус

4️⃣ Retrieving database properties details...
   • ID задания: title
   • Тема: select (10 options)
   • Уровень: select (3 options)
   • День цикла: select (5 options)
   • Номер в дне: select (3 options)

5️⃣ Available levels:
   • Beginner
   • Elementary
   • Advanced

6️⃣ Available themes:
   • Family and Friends
   • Daily Routine
   • Food and Drinks
   • Home
   • Hobbies
   ... and 5 more

7️⃣ Counting tasks...
   📊 Total tasks in database: 45
   📚 Beginner: 15 tasks
   📚 Elementary: 15 tasks
   📚 Advanced: 15 tasks

============================================================
✅ ALL TESTS PASSED!
============================================================

📝 Summary:
   • Database: English Learning Tasks
   • Total tasks: 45
   • Levels: 3
   • Themes: 10

🚀 Notion client is ready to use!
```

### Ошибки и их решения

#### ❌ Connection Error: object_not_found

```
❌ CONNECTION ERROR: Failed to retrieve database info: object_not_found - 
Could not find database with ID: xxx. Make sure the relevant pages and 
databases are shared with your integration.
```

**Решение:**
1. Проверьте `NOTION_DATABASE_ID` в `.env`
2. Откройте базу данных в Notion
3. Нажмите `...` → `Add connections` → выберите вашу интеграцию
4. Убедитесь, что интеграция имеет доступ

#### ❌ Connection Error: unauthorized

```
❌ CONNECTION ERROR: unauthorized - API token is invalid.
```

**Решение:**
1. Проверьте `NOTION_API_KEY` в `.env`
2. Перейдите в https://www.notion.so/my-integrations
3. Скопируйте Internal Integration Token
4. Вставьте в `.env` файл

---

## 🔧 Singleton Pattern

### Функция `get_notion_client()`

Для переиспользования одного экземпляра клиента во всем приложении используется паттерн Singleton.

```python
from database.notion_client import get_notion_client

# В любом месте приложения
notion = get_notion_client()
notion.test_connection()

# Везде будет использоваться один экземпляр
notion2 = get_notion_client()
assert notion is notion2  # True
```

**Преимущества:**
- Один экземпляр = одно подключение
- Экономия ресурсов
- Consistent state

---

## 📝 Примеры использования

### Базовая проверка подключения

```python
from database.notion_client import NotionClient

notion = NotionClient()

if notion.test_connection():
    print("Connected!")
    db_info = notion.get_database_info()
    print(f"Database: {db_info['title']}")
```

### Получение статистики

```python
from database.notion_client import get_notion_client

notion = get_notion_client()

# Общая статистика
total = notion.count_tasks()
print(f"Total tasks: {total}")

# По уровням
for level in notion.get_available_levels():
    count = notion.count_tasks(level=level)
    print(f"{level}: {count} tasks")
```

### Проверка структуры БД

```python
from database.notion_client import get_notion_client

notion = get_notion_client()
props = notion.get_database_properties()

# Проверка наличия обязательных полей
required_fields = ["ID задания", "Тема", "Уровень", "День цикла"]
for field in required_fields:
    if field in props:
        print(f"✅ {field}: {props[field]['type']}")
    else:
        print(f"❌ {field}: MISSING!")
```

---

## 🚀 Следующие шаги (Этап 2.2)

В следующем этапе будут реализованы методы для:

1. **Получение конкретного задания**
   - `get_task(level, theme_order, day, task_number)`
   - Парсинг всех полей Notion в Python объект

2. **Работа с темами**
   - `get_theme_info(level, theme_order)`
   - `get_next_theme_order(level, current_theme_order)`

3. **Обработка медиа**
   - Получение URL медиа-файлов
   - Определение типа медиа

4. **Кэширование**
   - Кэширование часто запрашиваемых данных
   - Инвалидация кэша

---

## 📊 Метрики

### Производительность

| Операция | Среднее время | Примечания |
|----------|---------------|------------|
| `test_connection()` | ~300ms | Один HTTP запрос |
| `get_database_info()` | ~300ms | Один HTTP запрос |
| `get_database_properties()` | ~300ms | Один HTTP запрос |
| `count_tasks()` (без фильтров) | ~500ms | С пагинацией |
| `count_tasks(level=...)` | ~400ms | С фильтром |

### Лимиты Notion API

- **Rate limit**: 3 requests per second (average)
- **Max requests**: ~1000 per minute
- **Page size**: 100 results per query

**Наши лимиты вписываются в ограничения Notion API.**

---

## ✅ Завершено

- [X] Создан файл `database/notion_client.py`
- [X] Реализован класс `NotionClient` с инициализацией
- [X] Реализована обработка ошибок подключения
- [X] Реализованы методы для получения информации о БД
- [X] Реализованы методы для подсчета заданий
- [X] Создан тестовый скрипт для проверки подключения
- [X] Добавлено логирование всех операций
- [X] Реализован паттерн Singleton
- [X] Создана документация

---

**Дата завершения:** 26 октября 2024  
**Следующий этап:** 2.2 - Получение заданий из Notion


