"""
Main Bot Module

Главный файл Telegram бота для изучения английского языка.
Настройка aiogram Bot, Dispatcher, FSM и handlers.

Author: Vladimir
Date: 2024-10-26
"""

import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from config.config import config
from database.db_manager import DatabaseManager
from database.notion_client import get_notion_client

# Импорт middleware
from bot.middlewares import (
    LoggingMiddleware,
    StateLoggingMiddleware,
    ErrorHandlerMiddleware
)

# Импорт handlers (будут созданы позже)
# from bot.handlers import start, tasks, progress, help_cmd


def setup_logging() -> None:
    """
    Настройка логирования с ротацией файлов.
    
    Логи пишутся:
    - В консоль (INFO и выше)
    - В файл bot.log с ротацией (DEBUG и выше)
    
    Ротация файлов:
    - Максимальный размер файла: 10 MB
    - Хранится максимум 5 файлов
    """
    # Создаем форматтер
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настройка root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Удаляем существующие handlers (если есть)
    root_logger.handlers.clear()
    
    # Handler для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # Handler для файла с ротацией
    try:
        file_handler = RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        root_logger.addHandler(file_handler)
    except Exception as e:
        root_logger.warning(f"Failed to setup file logging: {e}")
    
    # Снижаем уровень логирования для некоторых библиотек
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def setup_dispatcher() -> Dispatcher:
    """
    Настройка Dispatcher с FSM и middleware.
    
    Returns:
        Настроенный Dispatcher
    """
    # Создаем FSM storage (в памяти для простоты)
    # Для production рекомендуется использовать Redis
    storage = MemoryStorage()
    
    # Создаем Dispatcher
    dp = Dispatcher(storage=storage)
    
    # Регистрируем middleware
    # Порядок важен: сначала логирование, потом обработка ошибок
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    dp.message.middleware(StateLoggingMiddleware())
    dp.callback_query.middleware(StateLoggingMiddleware())
    
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
    
    return dp


def setup_handlers(dp: Dispatcher) -> None:
    """
    Регистрация всех handlers бота.
    
    Args:
        dp: Dispatcher для регистрации handlers
    """
    # Импортируем и регистрируем handlers
    # Порядок важен: более специфичные handlers должны быть первыми
    
    from bot.handlers import start, tasks, progress, help_cmd
    
    # Регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(progress.router)
    dp.include_router(help_cmd.router)
    
    logging.info("✅ Handlers registered successfully")


async def on_startup(bot: Bot) -> None:
    """
    Действия при запуске бота.
    
    Args:
        bot: Экземпляр бота
    """
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("🤖 TELEGRAM BOT STARTING...")
    logger.info("=" * 60)
    
    # Проверка конфигурации
    try:
        config.validate()
        logger.info("✅ Configuration validated")
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        raise
    
    # Инициализация базы данных
    try:
        db = DatabaseManager(config.SQLITE_DB_PATH)
        db_info = db.check_tables()
        
        if not db_info['db_exists']:
            logger.warning("⚠️  Database not found, initializing...")
            db.init_database()
        
        logger.info(f"✅ Database ready: {len(db_info['tables'])} tables")
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise
    
    # Проверка подключения к Notion
    try:
        notion = get_notion_client()
        if notion.test_connection():
            db_info = notion.get_database_info()
            logger.info(f"✅ Notion connected: '{db_info['title']}'")
        else:
            logger.error("❌ Failed to connect to Notion")
            raise ConnectionError("Notion connection failed")
            
    except Exception as e:
        logger.error(f"❌ Notion connection error: {e}")
        raise
    
    # Получение информации о боте
    try:
        me = await bot.get_me()
        logger.info(f"✅ Bot info: @{me.username} ({me.first_name})")
    except Exception as e:
        logger.error(f"❌ Failed to get bot info: {e}")
        raise
    
    logger.info("=" * 60)
    logger.info("🚀 BOT STARTED SUCCESSFULLY!")
    logger.info("=" * 60)


async def on_shutdown(bot: Bot) -> None:
    """
    Действия при остановке бота.
    
    Args:
        bot: Экземпляр бота
    """
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("🛑 SHUTTING DOWN BOT...")
    logger.info("=" * 60)
    
    # Закрываем сессию бота
    await bot.session.close()
    
    logger.info("✅ Bot session closed")
    logger.info("👋 Goodbye!")


async def main() -> None:
    """
    Главная функция запуска бота.
    
    Настраивает логирование, инициализирует бота и Dispatcher,
    регистрирует handlers и запускает polling.
    """
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Создание бота
        bot = Bot(
            token=config.TELEGRAM_BOT_TOKEN,
            parse_mode=ParseMode.HTML  # Используем HTML для форматирования
        )
        
        # Настройка Dispatcher
        dp = setup_dispatcher()
        
        # Регистрация handlers
        setup_handlers(dp)
        
        # Регистрация startup и shutdown handlers
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Запуск polling
        logger.info("Starting polling...")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True  # Пропускаем старые сообщения
        )
        
    except KeyboardInterrupt:
        logger.info("⌨️  Received keyboard interrupt")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    """
    Точка входа в приложение.
    
    Запуск: python -m bot.main
    """
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

