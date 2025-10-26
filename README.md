# English Learning Telegram Bot 🇬🇧

Telegram-бот для ежедневной практики английского языка с заданиями из Notion.

## 📋 Описание

Бот помогает ученикам поддерживать регулярное обучение, отправляя **три коротких задания в день** (на 5-10 минут). Бот работает по **5-дневному тематическому циклу**, где каждый день посвящен одному типу заданий.

### Как это работает

- **1 тема** = 5 дней обучения = 15 заданий
- **День 1**: 3 задания на Grammar (грамматика)
- **День 2**: 3 задания на Reading (чтение)
- **День 3**: 3 задания на Vocabulary (словарный запас)
- **День 4**: 3 задания на Situations (жизненные ситуации)
- **День 5**: 3 задания на Review (повторение)

После завершения одной темы автоматически начинается следующая!

## ✨ Возможности

### Для учеников:
- ✅ Выбор уровня сложности (Beginner / Elementary / Advanced)
- ✅ Ежедневная автоматическая рассылка заданий
- ✅ Задания с автопроверкой (multiple choice)
- ✅ Открытые вопросы с проверкой преподавателем
- ✅ Отслеживание прогресса и статистики
- ✅ Мотивационные сообщения
- ✅ Медиа-контент (картинки, аудио, видео)

### Для преподавателей:
- ✅ Веб-интерфейс для проверки ответов учеников
- ✅ Хранение заданий в Notion (удобное редактирование)
- ✅ Генератор заданий через GPT-4
- ✅ Аналитика по пользователям

## 🛠 Технологии

- **Python 3.11+**
- **aiogram 3.x** - Telegram Bot API
- **Notion API** - хранение заданий
- **SQLite** - прогресс пользователей
- **OpenAI API** - генерация заданий
- **APScheduler** - автоматические рассылки
- **Flask** - веб-интерфейс для преподавателя

## 📁 Структура проекта

```
bro_cademy_bot/
├── bot/
│   ├── main.py              # Главный файл бота
│   ├── handlers/            # Обработчики команд
│   ├── tasks.py             # Логика заданий
│   └── scheduler.py         # Ежедневная рассылка
├── database/
│   ├── db_manager.py        # Работа с SQLite
│   └── notion_client.py     # Работа с Notion API
├── web/
│   ├── app.py               # Flask приложение
│   └── templates/           # HTML шаблоны
├── scripts/
│   └── generate_tasks.py    # Генерация заданий через GPT
├── config/
│   └── config.py            # Конфигурация
├── docs/
│   ├── NOTION_DB_STRUCTURE.md    # Структура БД Notion
│   ├── DATABASE_SCHEMA.md        # Схема SQLite
│   ├── THEMES_CATALOG.md         # Каталог тем
│   ├── QUICK_START_NOTION.md     # Быстрый старт Notion
│   └── roadmap.md               # Дорожная карта
├── .env.example             # Пример переменных окружения
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/bro_cademy_bot.git
cd bro_cademy_bot
```

### 2. Установка зависимостей

```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# venv\Scripts\activate   # для Windows

pip install -r requirements.txt
```

### 3. Настройка Notion

Следуйте подробной инструкции: [docs/QUICK_START_NOTION.md](docs/QUICK_START_NOTION.md)

Кратко:
1. Создайте базу данных в Notion
2. Настройте все необходимые поля
3. Создайте интеграцию и получите API ключ
4. Заполните минимум 1 тему (15 заданий)

### 4. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните:

```env
# Notion API
NOTION_API_KEY=secret_ваш_токен
NOTION_DATABASE_ID=ваш_database_id

# Telegram Bot
TELEGRAM_BOT_TOKEN=ваш_bot_token

# OpenAI API (опционально, для генерации заданий)
OPENAI_API_KEY=sk-ваш_ключ

# Планировщик
SCHEDULER_START_TIME=09:00
SCHEDULER_END_TIME=10:30
```

### 5. Инициализация базы данных

```bash
python -m database.db_manager
```

### 6. Запуск бота

```bash
python -m bot.main
```

### 7. Запуск веб-интерфейса (опционально)

В отдельном терминале:

```bash
python -m web.app
```

Откройте браузер: http://localhost:5000

## 📚 Документация

- **[roadmap.md](docs/roadmap.md)** - 📋 Дорожная карта разработки (пошаговый план)
- **[DATABASE_IMPLEMENTATION.md](docs/DATABASE_IMPLEMENTATION.md)** - ✅ Реализация SQLite базы данных (Этап 1.1)
- **[CRUD_IMPLEMENTATION.md](docs/CRUD_IMPLEMENTATION.md)** - ✅ CRUD операции для пользователей (Этап 1.2)
- **[PROGRESS_IMPLEMENTATION.md](docs/PROGRESS_IMPLEMENTATION.md)** - ✅ Работа с прогрессом пользователей (Этап 1.3)
- **[OPEN_ANSWERS_IMPLEMENTATION.md](docs/OPEN_ANSWERS_IMPLEMENTATION.md)** - ✅ Работа с открытыми вопросами (Этап 1.4)
- **[NOTION_DB_STRUCTURE.md](docs/NOTION_DB_STRUCTURE.md)** - Детальная структура базы данных Notion
- **[DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)** - Схема SQLite базы данных
- **[QUICK_START_NOTION.md](docs/QUICK_START_NOTION.md)** - Быстрый старт с Notion

## 🎯 Команды бота

### Для учеников:
- `/start` - Начать работу с ботом и выбрать уровень
- `/task` - Получить текущее задание
- `/progress` - Посмотреть свой прогресс
- `/changelevel` - Изменить уровень сложности
- `/help` - Список всех команд
- `/about` - Информация о боте

### Для администраторов:
- `/stats` - Общая статистика бота
- `/broadcast` - Отправить сообщение всем пользователям

## 📊 Структура данных

### Notion Database (Задания)
- Хранение всех заданий по темам
- 15 заданий на тему (5 дней × 3 задания)
- Поддержка медиа-контента
- Гибкая фильтрация и редактирование

### SQLite Database (Пользователи)
- Профили пользователей и их прогресс
- История выполненных заданий
- Ответы на открытые вопросы
- Статистика и аналитика

Подробнее: [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)

## 🎨 Примеры тем

### Beginner (A1)
- Family and Friends
- Daily Routine
- Food and Drinks
- Home
- Hobbies

### Elementary (A2)
- Work and Career
- Travel and Tourism
- Health and Fitness
- Shopping
- Technology

### Advanced (B1-B2)
- Education
- Environment
- Social Issues
- Culture
- Business

## 🔧 Разработка

### Требования
- Python 3.11+
- SQLite 3
- Notion API key
- Telegram Bot Token

### Тестирование

```bash
# Установка dev-зависимостей
pip install -r requirements-dev.txt

# Запуск тестов
pytest

# Проверка кода
flake8 bot/ database/ web/
black bot/ database/ web/
```

### Генерация заданий через GPT

```bash
python -m scripts.generate_tasks
```

Следуйте инструкциям в интерактивном режиме.

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! 

1. Fork репозитория
2. Создайте ветку для фичи (`git checkout -b feature/AmazingFeature`)
3. Commit изменений (`git commit -m 'Add some AmazingFeature'`)
4. Push в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

## 📧 Контакты

- **Автор**: Vladimir
- **Telegram**: @yourusername
- **Email**: your.email@example.com

## 🙏 Благодарности

- [aiogram](https://github.com/aiogram/aiogram) - отличная библиотека для Telegram ботов
- [Notion API](https://developers.notion.com/) - мощный API для работы с данными
- Все контрибьюторы проекта

---

**⭐ Если проект вам полезен, поставьте звезду на GitHub!**

