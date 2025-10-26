"""
Configuration Module

Загрузка и управление конфигурацией приложения из переменных окружения.
"""

import os
from typing import List
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()


class Config:
    """Класс конфигурации приложения"""
    
    # Notion API
    NOTION_API_KEY: str = os.getenv("NOTION_API_KEY", "")
    NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID", "")
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Scheduler
    SCHEDULER_START_TIME: str = os.getenv("SCHEDULER_START_TIME", "09:00")
    SCHEDULER_END_TIME: str = os.getenv("SCHEDULER_END_TIME", "10:30")
    
    # Database
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "bot_database.db")
    
    # Flask
    FLASK_SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_HOST: str = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # Admin
    ADMIN_USER_IDS: List[int] = [
        int(uid.strip()) 
        for uid in os.getenv("ADMIN_USER_IDS", "").split(",") 
        if uid.strip()
    ]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")
    
    @classmethod
    def validate(cls) -> None:
        """
        Валидация обязательных переменных окружения.
        
        Raises:
            ValueError: Если не заполнены обязательные переменные.
        """
        required_vars = {
            "NOTION_API_KEY": cls.NOTION_API_KEY,
            "NOTION_DATABASE_ID": cls.NOTION_DATABASE_ID,
            "TELEGRAM_BOT_TOKEN": cls.TELEGRAM_BOT_TOKEN,
        }
        
        missing_vars = [name for name, value in required_vars.items() if not value]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please check your .env file."
            )
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """
        Проверка, является ли пользователь администратором.
        
        Args:
            user_id: Telegram ID пользователя
            
        Returns:
            True если пользователь администратор, иначе False
        """
        return user_id in cls.ADMIN_USER_IDS


# Создание экземпляра конфигурации
config = Config()


if __name__ == "__main__":
    # Тестирование конфигурации
    try:
        config.validate()
        print("✅ Configuration is valid!")
        print(f"Notion Database ID: {config.NOTION_DATABASE_ID[:10]}...")
        print(f"Telegram Bot Token: {config.TELEGRAM_BOT_TOKEN[:10]}...")
        print(f"Admin Users: {config.ADMIN_USER_IDS}")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")

