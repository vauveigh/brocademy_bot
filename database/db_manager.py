"""
Database Manager

Модуль для работы с SQLite базой данных.
Управляет пользователями, их прогрессом и ответами на задания.

Author: Vladimir
Date: 2024-10-26
"""

import sqlite3
import os
from typing import Optional, Tuple
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Менеджер для работы с SQLite базой данных"""
    
    def __init__(self, db_path: str = "bot_database.db"):
        """
        Инициализация менеджера базы данных.
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        logger.info(f"Инициализация DatabaseManager с БД: {db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Создать подключение к базе данных.
        
        Returns:
            Объект подключения к SQLite
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Доступ к колонкам по имени
        return conn
    
    def init_database(self) -> None:
        """
        Инициализация базы данных.
        Создает все необходимые таблицы и индексы.
        
        Raises:
            sqlite3.Error: При ошибке создания таблиц
        """
        logger.info("Начало инициализации базы данных...")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Создание таблицы users
            logger.info("Создание таблицы users...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    level TEXT NOT NULL,
                    current_day INTEGER DEFAULT 1,
                    current_theme TEXT,
                    theme_order INTEGER DEFAULT 1,
                    task_in_day INTEGER DEFAULT 1,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_task_date DATE
                )
            ''')
            
            # Создание таблицы user_progress
            logger.info("Создание таблицы user_progress...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    task_id TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    answer TEXT,
                    is_correct BOOLEAN,
                    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Создание таблицы user_answers
            logger.info("Создание таблицы user_answers...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    task_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    user_answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checked BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Создание индексов для users
            logger.info("Создание индексов для таблицы users...")
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_users_level 
                ON users(level)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_users_theme_order 
                ON users(theme_order)
            ''')
            
            # Создание индексов для user_progress
            logger.info("Создание индексов для таблицы user_progress...")
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_progress_user_id 
                ON user_progress(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_progress_task_id 
                ON user_progress(task_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_progress_answered_at 
                ON user_progress(answered_at)
            ''')
            
            # Создание индексов для user_answers
            logger.info("Создание индексов для таблицы user_answers...")
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_answers_user_id 
                ON user_answers(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_answers_checked 
                ON user_answers(checked)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_answers_created_at 
                ON user_answers(created_at)
            ''')
            
            conn.commit()
            logger.info("✅ База данных успешно инициализирована!")
            logger.info(f"📂 Файл базы данных: {os.path.abspath(self.db_path)}")
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при инициализации базы данных: {e}")
            raise
        finally:
            conn.close()
    
    def check_tables(self) -> dict:
        """
        Проверить наличие всех таблиц в базе данных.
        
        Returns:
            Словарь с информацией о таблицах
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Получить список всех таблиц
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Получить список всех индексов
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            
            # Подсчитать количество записей в каждой таблице
            table_counts = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_counts[table] = count
            
            return {
                'tables': tables,
                'indexes': indexes,
                'counts': table_counts,
                'db_file': os.path.abspath(self.db_path),
                'db_exists': os.path.exists(self.db_path),
                'db_size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            }
            
        finally:
            conn.close()
    
    def drop_all_tables(self) -> None:
        """
        ⚠️ ОСТОРОЖНО: Удалить все таблицы из базы данных.
        Используйте только для тестирования!
        """
        logger.warning("⚠️  Удаление всех таблиц...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Получить список всех таблиц
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Удалить каждую таблицу
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                logger.info(f"Удалена таблица: {table}")
            
            conn.commit()
            logger.info("✅ Все таблицы удалены")
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при удалении таблиц: {e}")
            raise
        finally:
            conn.close()


def init_database(db_path: str = "bot_database.db") -> None:
    """
    Удобная функция для быстрой инициализации базы данных.
    
    Args:
        db_path: Путь к файлу базы данных
        
    Example:
        >>> from database.db_manager import init_database
        >>> init_database()
    """
    db = DatabaseManager(db_path)
    db.init_database()


def main():
    """
    Главная функция для тестирования и инициализации БД.
    Запускается при выполнении: python -m database.db_manager
    """
    # Установка UTF-8 для Windows консоли
    import sys
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleCP(65001)
            kernel32.SetConsoleOutputCP(65001)
        except:
            pass
    
    print("=" * 60)
    print("🗄️  Database Manager - Инициализация SQLite базы данных")
    print("=" * 60)
    print()
    
    # Путь к БД из переменных окружения или по умолчанию
    from config.config import config
    db_path = config.SQLITE_DB_PATH
    
    # Создать менеджер
    db = DatabaseManager(db_path)
    
    # Проверить существует ли БД
    db_exists = os.path.exists(db_path)
    
    if db_exists:
        print(f"📂 База данных найдена: {os.path.abspath(db_path)}")
        print(f"📊 Размер: {os.path.getsize(db_path)} байт")
        print()
        
        # Показать текущее состояние
        info = db.check_tables()
        print(f"📋 Таблиц в БД: {len(info['tables'])}")
        for table in info['tables']:
            count = info['counts'][table]
            print(f"   - {table}: {count} записей")
        
        print(f"\n🔑 Индексов: {len(info['indexes'])}")
        for index in info['indexes']:
            print(f"   - {index}")
        
        print("\n" + "=" * 60)
        response = input("⚠️  БД уже существует. Пересоздать? (yes/no): ")
        
        if response.lower() in ['yes', 'y', 'да']:
            print("\n🗑️  Удаление старых таблиц...")
            db.drop_all_tables()
            print("📦 Создание новых таблиц...")
            db.init_database()
        else:
            print("ℹ️  Пропущено. БД не изменена.")
            return
    else:
        print(f"📂 База данных не найдена: {os.path.abspath(db_path)}")
        print("📦 Создание новой базы данных...")
        print()
        db.init_database()
    
    print()
    print("=" * 60)
    print("✅ Проверка созданной базы данных")
    print("=" * 60)
    print()
    
    # Показать итоговую информацию
    info = db.check_tables()
    
    print(f"📂 Файл: {info['db_file']}")
    print(f"📊 Размер: {info['db_size']} байт")
    print(f"✅ Существует: {'Да' if info['db_exists'] else 'Нет'}")
    print()
    
    print(f"📋 Таблицы ({len(info['tables'])}):")
    expected_tables = ['users', 'user_progress', 'user_answers']
    for table in expected_tables:
        if table in info['tables']:
            print(f"   ✅ {table}: {info['counts'][table]} записей")
        else:
            print(f"   ❌ {table}: НЕ НАЙДЕНА!")
    
    print()
    print(f"🔑 Индексы ({len(info['indexes'])}):")
    expected_indexes = [
        'idx_users_level', 'idx_users_theme_order',
        'idx_progress_user_id', 'idx_progress_task_id', 'idx_progress_answered_at',
        'idx_answers_user_id', 'idx_answers_checked', 'idx_answers_created_at'
    ]
    for index in expected_indexes:
        if index in info['indexes']:
            print(f"   ✅ {index}")
        else:
            print(f"   ❌ {index}: НЕ НАЙДЕН!")
    
    print()
    print("=" * 60)
    
    # Финальная проверка
    all_tables_ok = all(table in info['tables'] for table in expected_tables)
    all_indexes_ok = all(index in info['indexes'] for index in expected_indexes)
    
    if all_tables_ok and all_indexes_ok:
        print("🎉 УСПЕХ! База данных полностью готова к использованию!")
    else:
        print("⚠️  ВНИМАНИЕ: Некоторые таблицы или индексы отсутствуют!")
    
    print("=" * 60)


if __name__ == "__main__":
    main()

