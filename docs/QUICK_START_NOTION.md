# Быстрый старт: Создание базы данных Notion

## Шаг 1: Создание базы данных

1. Откройте Notion и создайте новую страницу
2. Добавьте на страницу **Database - Full Page**
3. Назовите базу данных: **"English Bot Tasks"** или любое другое имя

## Шаг 2: Настройка полей (Properties)

Удалите все стандартные поля кроме **Title** и создайте следующие поля:

### Переименуйте Title
- **Name**: переименуйте в **"ID задания"**
- Это будет основное поле с ID в формате: `BEG-FAMILY-D1-G1`

### Создайте новые поля (Add Property):

| Название поля | Тип (Type) | Опции (для Select) |
|--------------|-----------|-------------------|
| **Тема** | Select | *(создайте опции для каждой темы)* |
| **Порядок темы** | Number | - |
| **Уровень** | Select | Beginner, Elementary, Advanced |
| **Тип задания** | Select | grammar, reading, vocabulary, situations, review |
| **День цикла** | Select | 1, 2, 3, 4, 5 |
| **Номер в дне** | Select | 1, 2, 3 |
| **Вопрос** | Text | - |
| **Тип ответа** | Select | multiple_choice, open_question |
| **Варианты ответов** | Text | - |
| **Правильный ответ** | Text | - |
| **Объяснение** | Text | - |
| **URL медиа** | URL | - |
| **Тип медиа** | Select | none, image, audio, video |
| **Статус** | Select | draft, active, archived |

### Автоматические поля:
- **Created time** - добавляется автоматически
- **Last edited time** - добавляется автоматически

## Шаг 3: Создание первого задания (пример)

Нажмите **New** и заполните поля:

```
ID задания: BEG-FAMILY-D1-G1
Тема: Family and Friends
Порядок темы: 1
Уровень: Beginner
Тип задания: grammar
День цикла: 1
Номер в дне: 1
Вопрос: Choose the correct possessive adjective: "This is ___ brother."
Тип ответа: multiple_choice
Варианты ответов: my | mine | me | I
Правильный ответ: my
Объяснение: We use "my" before nouns to show possession. "Mine" is used without a noun.
URL медиа: [оставьте пустым]
Тип медиа: none
Статус: active
```

## Шаг 4: Получение API ключа

1. Перейдите на [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Нажмите **+ New integration**
3. Заполните:
   - **Name**: "English Bot"
   - **Associated workspace**: выберите ваш workspace
   - **Type**: Internal
4. Нажмите **Submit**
5. Скопируйте **Internal Integration Token** (начинается с `secret_...`)

## Шаг 5: Предоставление доступа к базе данных

1. Откройте вашу базу данных "English Bot Tasks" в Notion
2. Нажмите на **⋯** (три точки) в правом верхнем углу
3. Выберите **+ Add connections**
4. Найдите и выберите вашу интеграцию "English Bot"
5. Нажмите **Confirm**

## Шаг 6: Получение Database ID

Database ID находится в URL вашей базы данных:

```
https://www.notion.so/workspace-name/DATABASE_ID?v=...
                                      ^^^^^^^^^^^^
                                      Это ваш Database ID
```

Пример:
```
URL: https://www.notion.so/myworkspace/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6?v=...
Database ID: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Важно**: Database ID — это 32-символьная строка без дефисов.

## Шаг 7: Настройка .env файла

Создайте файл `.env` в корне проекта и добавьте:

```env
# Notion API
NOTION_API_KEY=secret_ваш_токен_здесь
NOTION_DATABASE_ID=ваш_database_id_здесь

# Telegram Bot
TELEGRAM_BOT_TOKEN=ваш_telegram_bot_token

# OpenAI API (для генерации заданий)
OPENAI_API_KEY=sk-ваш_openai_ключ
```

## Шаг 8: Заполнение первой темы

Для полноценной работы создайте 15 заданий для одной темы:

### Тема: "Family and Friends" (Beginner, Порядок: 1)

**День 1 - Grammar (3 задания):**
- `BEG-FAMILY-D1-G1` - Possessive adjectives
- `BEG-FAMILY-D1-G2` - To be (am/is/are) with family members
- `BEG-FAMILY-D1-G3` - Have/Has with family

**День 2 - Reading (3 задания):**
- `BEG-FAMILY-D2-R1` - Short text about a family
- `BEG-FAMILY-D2-R2` - Dialogue between family members
- `BEG-FAMILY-D2-R3` - Description of a friend

**День 3 - Vocabulary (3 задания):**
- `BEG-FAMILY-D3-V1` - Family members words
- `BEG-FAMILY-D3-V2` - Adjectives to describe people
- `BEG-FAMILY-D3-V3` - Relationships

**День 4 - Situations (3 задания):**
- `BEG-FAMILY-D4-S1` - Introducing family members
- `BEG-FAMILY-D4-S2` - Talking about your friend
- `BEG-FAMILY-D4-S3` - Describing someone

**День 5 - Review (3 задания):**
- `BEG-FAMILY-D5-RV1` - Mixed grammar + vocabulary
- `BEG-FAMILY-D5-RV2` - Reading comprehension
- `BEG-FAMILY-D5-RV3` - Open question: "Describe your family"

## Шаг 9: Тестирование API подключения

Создайте тестовый скрипт `test_notion.py`:

```python
import os
from notion_client import Client
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация Notion клиента
notion = Client(auth=os.getenv("NOTION_API_KEY"))
database_id = os.getenv("NOTION_DATABASE_ID")

# Тестовый запрос: получить все задания
try:
    response = notion.databases.query(
        database_id=database_id,
        filter={
            "and": [
                {"property": "Уровень", "select": {"equals": "Beginner"}},
                {"property": "Статус", "select": {"equals": "active"}}
            ]
        }
    )
    
    print(f"✅ Подключение успешно!")
    print(f"Найдено заданий: {len(response['results'])}")
    
    # Показать первое задание
    if response['results']:
        first_task = response['results'][0]
        task_id = first_task['properties']['ID задания']['title'][0]['plain_text']
        print(f"\nПервое задание: {task_id}")
        
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
```

Запустите:
```bash
python test_notion.py
```

Если видите `✅ Подключение успешно!` — всё работает!

## Шаг 10: Организация работы

### Используйте Views (Представления) в Notion:

1. **All Tasks** (Table) - все задания
2. **By Level** (Board) - группировка по уровню
3. **By Theme** (Board) - группировка по теме
4. **Draft Only** (Table) - только черновики
5. **Calendar** (Calendar) - по дате создания

### Фильтры для удобства:

**Активные задания одного уровня:**
```
Уровень = Beginner
Статус = active
```

**Одна тема для проверки:**
```
Тема = Family and Friends
Порядок темы = 1
Сортировка: День цикла (по возрастанию), затем Номер в дне
```

**Незавершенные задания:**
```
Статус = draft
```

## Полезные советы

### 1. Шаблоны заданий
Создайте template-страницу с примерами всех типов заданий для копирования.

### 2. Дублирование заданий
Используйте **Duplicate** для создания похожих заданий (особенно полезно для одной темы).

### 3. Bulk Edit
Выделите несколько записей и измените общие поля (например, установите всем `Статус = active`).

### 4. Import/Export
- Export в CSV для резервной копии
- Import из CSV для массового добавления

### 5. Relation (опционально)
Можно создать отдельную таблицу "Темы" и связать через Relation для лучшей организации.

## Чеклист готовности

Перед запуском бота убедитесь:

- [ ] База данных создана в Notion
- [ ] Все поля настроены с правильными типами
- [ ] API интеграция создана и подключена к базе
- [ ] NOTION_API_KEY добавлен в .env
- [ ] NOTION_DATABASE_ID добавлен в .env
- [ ] Тестовое подключение работает
- [ ] Создана минимум 1 полная тема (15 заданий)
- [ ] Все задания имеют `Статус = active`
- [ ] Проверена правильность форматирования "Варианты ответов" (разделитель `|`)
- [ ] Правильные ответы точно совпадают с вариантами

## Следующие шаги

После настройки Notion:
1. Настройте SQLite базу данных (см. `DATABASE_SCHEMA.md`)
2. Изучите каталог тем (см. `THEMES_CATALOG.md`)
3. Начните разработку бота (см. `roadmap.md`)

---

## Часто задаваемые вопросы

**Q: Можно ли использовать бесплатный план Notion?**  
A: Да, бесплатного плана достаточно для хранения всех заданий.

**Q: Как добавить картинки в задания?**  
A: Загрузите картинку в любое облачное хранилище (Imgur, Google Drive с публичным доступом) и вставьте URL в поле "URL медиа".

**Q: Можно ли редактировать задания после того, как пользователи их выполнили?**  
A: Да, но изменения не повлияют на уже выполненные задания (они сохранены в SQLite).

**Q: Как архивировать старые задания?**  
A: Измените `Статус` на `archived` — они перестанут показываться пользователям.

**Q: Сколько заданий нужно для старта?**  
A: Минимум 1 тема (15 заданий) для одного уровня. Для комфортной работы — 3-5 тем (45-75 заданий).

**Q: Можно ли использовать русский язык в вопросах?**  
A: Технически да, но рекомендуется использовать английский для погружения в языковую среду.

---

Подробная информация о структуре: `NOTION_DB_STRUCTURE.md`

