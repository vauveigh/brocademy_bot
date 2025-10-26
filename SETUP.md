# Инструкция по настройке проекта

## 1. Клонирование репозитория

Если вы еще не клонировали репозиторий:

```bash
git clone https://github.com/yourusername/bro_cademy_bot.git
cd bro_cademy_bot
```

## 2. Создание виртуального окружения

### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Настройка переменных окружения

Файл `.env` уже создан в корне проекта. Заполните следующие обязательные поля:

```env
# Notion API (получите из https://www.notion.so/my-integrations)
NOTION_API_KEY=secret_ваш_токен_здесь
NOTION_DATABASE_ID=ваш_database_id_здесь

# Telegram Bot (получите от @BotFather)
TELEGRAM_BOT_TOKEN=ваш_bot_token_здесь

# OpenAI API (опционально, для генерации заданий)
OPENAI_API_KEY=sk-ваш_ключ_здесь

# Admin User IDs (ваш Telegram user ID)
ADMIN_USER_IDS=ваш_user_id_здесь
```

### Как получить свой Telegram User ID:
1. Напишите боту [@userinfobot](https://t.me/userinfobot)
2. Он отправит вам ваш ID

## 5. Проверка конфигурации

Запустите тест конфигурации:

```bash
python -m config.config
```

Вы должны увидеть:
```
✅ Configuration is valid!
```

## 6. Инициализация базы данных

После создания `database/db_manager.py` (Этап 1 roadmap), запустите:

```bash
python -m database.db_manager
```

## 7. Тестирование подключения к Notion

После создания `database/notion_client.py` (Этап 2 roadmap), запустите:

```bash
python docs/QUICK_START_NOTION.md  # смотрите тестовый скрипт в документации
```

## 8. Запуск бота

После завершения разработки (Этапы 1-4):

```bash
python -m bot.main
```

## 9. Запуск веб-интерфейса

После завершения Этапа 7:

```bash
python -m web.app
```

Откройте браузер: http://localhost:5000

---

## Структура проекта

```
bro_cademy_bot/
├── bot/                    # Telegram бот
│   ├── __init__.py
│   ├── main.py            # (создать в Этапе 3)
│   ├── handlers/          # (создать позже)
│   ├── tasks.py           # (создать в Этапе 4)
│   └── scheduler.py       # (создать в Этапе 6)
├── database/              # Работа с БД
│   ├── __init__.py
│   ├── db_manager.py      # (создать в Этапе 1)
│   └── notion_client.py   # (создать в Этапе 2)
├── web/                   # Flask веб-интерфейс
│   ├── __init__.py
│   ├── app.py             # (создать в Этапе 7)
│   └── templates/         # (создать позже)
├── scripts/               # Вспомогательные скрипты
│   ├── __init__.py
│   └── generate_tasks.py  # (создать в Этапе 8)
├── config/                # Конфигурация
│   ├── __init__.py
│   └── config.py          # ✅ Создан
├── docs/                  # Документация
│   ├── roadmap.md
│   ├── NOTION_DB_STRUCTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── QUICK_START_NOTION.md
│   └── SUMMARY.md
├── .env                   # ✅ Создан (заполните!)
├── .gitignore             # ✅ Создан
├── env.example            # ✅ Шаблон
├── requirements.txt       # ✅ Зависимости
├── README.md              # ✅ Главная страница
└── SETUP.md               # ✅ Эта инструкция
```

---

## Troubleshooting

### Проблема: "Module not found"
**Решение**: Убедитесь, что виртуальное окружение активировано и зависимости установлены:
```bash
pip list
```

### Проблема: "Configuration error: Missing required environment variables"
**Решение**: Проверьте файл `.env` и заполните все обязательные поля.

### Проблема: "Cannot connect to Notion"
**Решение**: 
1. Проверьте правильность `NOTION_API_KEY`
2. Проверьте правильность `NOTION_DATABASE_ID`
3. Убедитесь, что интеграция имеет доступ к базе данных

### Проблема: "Telegram bot not responding"
**Решение**:
1. Проверьте `TELEGRAM_BOT_TOKEN`
2. Убедитесь, что бот не заблокирован
3. Проверьте логи: `tail -f bot.log`

---

## Следующие шаги

После завершения настройки следуйте roadmap:

1. **Этап 1**: Создайте `database/db_manager.py`
2. **Этап 2**: Создайте `database/notion_client.py`
3. **Этап 3**: Создайте `bot/main.py`
4. И так далее...

Подробный план в [docs/roadmap.md](docs/roadmap.md)

---

**Удачи в разработке! 🚀**

