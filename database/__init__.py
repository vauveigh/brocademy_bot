"""
Database Package

Модуль для работы с базой данных SQLite.

Основные компоненты:
- DatabaseManager: класс для управления базой данных
- init_database(): функция для быстрой инициализации БД

Example:
    >>> from database import init_database
    >>> init_database()
    
Author: Vladimir
Date: 2024-10-26
"""

from .db_manager import DatabaseManager, init_database

__all__ = ['DatabaseManager', 'init_database']
