# Changelog

Все значимые изменения в проекте документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/),
и проект следует [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- SQLite база данных с 3 таблицами:
  - users: информация о пользователях и прогрессе
  - user_progress: история выполнения заданий
  - user_answers: ответы на открытые вопросы
- DatabaseManager класс для работы с БД
- 8 индексов для оптимизации запросов
- Функции инициализации и проверки БД
- Тестовый скрипт для создания и проверки базы данных

### Planned
- Этап 1.2: CRUD операции для пользователей
- Этап 2: Notion API integration
- Этап 3: Basic bot functionality

## [0.1.0] - 2024-10-26

### Added
- Структура проекта (bot/, database/, config/, web/, scripts/)
- Система конфигурации с валидацией (config/config.py)
- Полная документация проекта:
  - docs/NOTION_DB_STRUCTURE.md - структура БД Notion
  - docs/DATABASE_SCHEMA.md - схема SQLite
  - docs/QUICK_START_NOTION.md - инструкция по настройке Notion
  - docs/roadmap.md - план разработки (12 этапов, 200+ задач)
  - docs/SUMMARY.md - сводная документация
  - SETUP.md - инструкция по настройке проекта
  - README.md - главная страница проекта
- Mock-up тема "Family and Friends" с 15 заданиями
- CSV файл для импорта заданий в Notion
- Инструкции по импорту (IMPORT_INSTRUCTIONS.md)
- Инструкции по настройке Select опций (NOTION_SELECT_SETUP.md)
- Файлы конфигурации:
  - requirements.txt - все зависимости Python
  - env.example - шаблон переменных окружения
  - .gitignore - исключения для Git

### Documentation
- Детальная структура 15+ полей Notion Database
- Примеры заданий для всех типов (grammar, reading, vocabulary, situations, review)
- Рекомендации по созданию контента
- Схема SQLite с 3 таблицами и примерами запросов
- Инструкции по миграции и бэкапу данных
- Список из 30 рекомендованных тем (10 на уровень)

### Infrastructure
- Виртуальное окружение Python настроено
- Все зависимости установлены
- Токены и ключи настроены в .env

## [0.0.1] - 2024-10-25

### Added
- Инициализация проекта
- Создание базы данных в Notion
- Настройка Notion API интеграции (получены ключи)
- Регистрация Telegram бота через @BotFather
- Получение всех необходимых токенов