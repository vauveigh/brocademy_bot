# 📥 Инструкция по импорту заданий в Notion

## Файл для импорта

✅ **Создан:** `notion_tasks_family_friends.csv`  
📋 **Содержит:** 15 заданий для темы "Family and Friends" (Beginner, уровень 1)

---

## ⚠️ Важно: Создайте Select опции для поля "Тема"

**Перед импортом CSV** необходимо создать хотя бы одну Select опцию!

### Быстрая настройка (1 минута):

1. Откройте базу данных в Notion
2. Кликните на поле **"Тема"** → **"Edit property"**
3. Нажмите **"+ Add an option"**
4. Введите: **"Family and Friends"**
5. Сохраните

**Готово!** Теперь можно импортировать CSV.

📚 **Подробная инструкция:** [NOTION_SELECT_SETUP.md](NOTION_SELECT_SETUP.md) - список всех 30 тем

---

## 🚀 Способ 1: Импорт CSV в Notion (рекомендуется)

### Шаг 1: Откройте вашу базу данных Notion

Перейдите к базе данных **"English Bot Tasks"**

### Шаг 2: Откройте меню импорта

1. Нажмите на **⋯** (три точки) в правом верхнем углу базы данных
2. Выберите **"Import"** или **"Импорт"**

### Шаг 3: Выберите CSV файл

1. В открывшемся окне выберите **"CSV"**
2. Нажмите **"Choose file"** или перетащите файл `notion_tasks_family_friends.csv`
3. Выберите файл из корня проекта

### Шаг 4: Настройте импорт

Notion покажет preview данных:

1. **Merge with existing database** - выберите вашу базу "English Bot Tasks"
2. **First row is header** - убедитесь что галочка стоит ✅
3. Проверьте что столбцы правильно распознаны

### Шаг 5: Импортируйте

1. Нажмите **"Import"**
2. Дождитесь завершения (несколько секунд)
3. ✅ Готово! Все 15 заданий добавлены

---

## 📋 Способ 2: Ручное копирование (если импорт не работает)

Откройте файл `notion_tasks_family_friends.csv` и скопируйте данные построчно в Notion.

Для каждой строки:
1. Нажмите **"New"** в базе данных
2. Скопируйте значения из CSV в соответствующие поля
3. Сохраните

---

## ✅ Проверка после импорта

### 1. Откройте базу данных в Notion

Вы должны увидеть 15 новых записей:
- BEG-FAMILY-D1-G1
- BEG-FAMILY-D1-G2
- BEG-FAMILY-D1-G3
- ... (всего 15)

### 2. Проверьте фильтры

Создайте тестовый фильтр:
- **Уровень** = Beginner
- **Тема** = Family and Friends
- **Статус** = active

Должно показать все 15 заданий.

### 3. Проверьте распределение

- **День 1** (Grammar): 3 задания
- **День 2** (Reading): 3 задания
- **День 3** (Vocabulary): 3 задания
- **День 4** (Situations): 3 задания
- **День 5** (Review): 3 задания

### 4. Проверьте поля

Убедитесь что все поля заполнены:
- ✅ ID задания
- ✅ Тема
- ✅ Порядок темы
- ✅ Уровень
- ✅ Тип задания
- ✅ День цикла
- ✅ Номер в дне
- ✅ Вопрос
- ✅ Тип ответа
- ✅ Варианты ответов (для multiple_choice)
- ✅ Правильный ответ
- ✅ Объяснение (может быть пустым)
- ✅ Статус = active

---

## 🧪 Тестирование через API

После импорта проверьте подключение:

```python
# test_notion_import.py
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_API_KEY"))
database_id = os.getenv("NOTION_DATABASE_ID")

# Запрос первого задания темы
response = notion.databases.query(
    database_id=database_id,
    filter={
        "and": [
            {"property": "Уровень", "select": {"equals": "Beginner"}},
            {"property": "Порядок темы", "number": {"equals": 1}},
            {"property": "День цикла", "select": {"equals": "1"}},
            {"property": "Номер в дне", "select": {"equals": "1"}},
            {"property": "Статус", "select": {"equals": "active"}}
        ]
    }
)

if response['results']:
    task = response['results'][0]
    task_id = task['properties']['ID задания']['title'][0]['plain_text']
    print(f"✅ Найдено задание: {task_id}")
    print(f"📝 Вопрос: {task['properties']['Вопрос']['rich_text'][0]['plain_text']}")
    print("\n✅ Импорт успешен! Можно начинать разработку!")
else:
    print("❌ Задание не найдено. Проверьте импорт.")
```

Запустите:
```bash
python test_notion_import.py
```

---

## 🎨 Рекомендации по отображению в Notion

### Создайте Views для удобства:

#### 1. **View "By Day"** (Board)
- Группировка: День цикла
- Фильтр: Тема = Family and Friends
- Сортировка: Номер в дне

#### 2. **View "By Type"** (Board)
- Группировка: Тип задания
- Фильтр: Статус = active

#### 3. **View "All Tasks"** (Table)
- Все задания без фильтров
- Сортировка: Порядок темы → День цикла → Номер в дне

---

## 🚨 Troubleshooting

### Проблема: "Import failed"
**Решение:** 
- Проверьте что CSV файл корректный (откройте в текстовом редакторе)
- Убедитесь что поля в базе данных уже созданы
- Попробуйте импортировать построчно

### Проблема: "Column mismatch"
**Решение:**
- Названия полей в CSV должны точно совпадать с полями в Notion
- Проверьте язык (все поля на русском)
- Пересоздайте поля если нужно

### Проблема: "Не все поля импортировались"
**Решение:**
- После импорта вручную заполните пропущенные поля
- Notion может пропускать пустые ячейки

---

## 📊 Структура темы "Family and Friends"

### День 1: Grammar
- BEG-FAMILY-D1-G1 - Possessive adjectives
- BEG-FAMILY-D1-G2 - Verb "to be"
- BEG-FAMILY-D1-G3 - Have/has

### День 2: Reading
- BEG-FAMILY-D2-R1 - Family description
- BEG-FAMILY-D2-R2 - Friend description
- BEG-FAMILY-D2-R3 - Dialogue about siblings

### День 3: Vocabulary
- BEG-FAMILY-D3-V1 - Family members (grandmother)
- BEG-FAMILY-D3-V2 - Adjectives (funny)
- BEG-FAMILY-D3-V3 - Family members (uncle)

### День 4: Situations
- BEG-FAMILY-D4-S1 - Answering about siblings
- BEG-FAMILY-D4-S2 - Introducing family
- BEG-FAMILY-D4-S3 - Talking about living situation

### День 5: Review
- BEG-FAMILY-D5-RV1 - Mixed grammar
- BEG-FAMILY-D5-RV2 - Text completion
- BEG-FAMILY-D5-RV3 - Open question (writing)

**Всего:** 15 заданий ✨

---

## ✅ После успешного импорта

🎉 **Этап 0 ПОЛНОСТЬЮ ЗАВЕРШЕН!**

Можно переходить к:
- **Этап 1**: Создание базы данных SQLite
- **Этап 2**: Интеграция с Notion API
- **Этап 3**: Разработка бота

---

**Удачи с импортом!** 🚀

Если возникнут проблемы - обращайтесь!

