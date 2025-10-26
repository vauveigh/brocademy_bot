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
    
    # ==================== CRUD операции для пользователей ====================
    
    def create_user(self, user_id: int, username: Optional[str] = None, level: str = "Beginner") -> bool:
        """
        Создать нового пользователя в базе данных.
        
        Args:
            user_id: Telegram ID пользователя
            username: Telegram username пользователя (может быть None)
            level: Уровень сложности (Beginner/Elementary/Advanced)
            
        Returns:
            True если пользователь создан, False если уже существует
            
        Raises:
            ValueError: Если level не является допустимым значением
            sqlite3.Error: При ошибке БД
            
        Example:
            >>> db = DatabaseManager()
            >>> db.create_user(123456789, "john_doe", "Beginner")
            True
        """
        # Валидация уровня
        valid_levels = ["Beginner", "Elementary", "Advanced"]
        if level not in valid_levels:
            raise ValueError(f"Недопустимый уровень: {level}. Допустимые: {valid_levels}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Проверить, существует ли пользователь
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                logger.info(f"Пользователь {user_id} уже существует")
                return False
            
            # Создать нового пользователя
            cursor.execute("""
                INSERT INTO users (user_id, username, level, current_day, theme_order, task_in_day)
                VALUES (?, ?, ?, 1, 1, 1)
            """, (user_id, username, level))
            
            conn.commit()
            logger.info(f"✅ Создан пользователь: {user_id} ({username}) - уровень {level}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при создании пользователя {user_id}: {e}")
            raise
        finally:
            conn.close()
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """
        Получить информацию о пользователе.
        
        Args:
            user_id: Telegram ID пользователя
            
        Returns:
            Словарь с данными пользователя или None если не найден
            
        Example:
            >>> db = DatabaseManager()
            >>> user = db.get_user(123456789)
            >>> print(user['level'])
            'Beginner'
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            else:
                logger.info(f"Пользователь {user_id} не найден")
                return None
                
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при получении пользователя {user_id}: {e}")
            raise
        finally:
            conn.close()
    
    def update_user_level(self, user_id: int, level: str) -> bool:
        """
        Обновить уровень сложности пользователя.
        При смене уровня прогресс сбрасывается на начало.
        
        Args:
            user_id: Telegram ID пользователя
            level: Новый уровень (Beginner/Elementary/Advanced)
            
        Returns:
            True если обновление успешно, False если пользователь не найден
            
        Raises:
            ValueError: Если level не является допустимым значением
            
        Example:
            >>> db = DatabaseManager()
            >>> db.update_user_level(123456789, "Elementary")
            True
        """
        # Валидация уровня
        valid_levels = ["Beginner", "Elementary", "Advanced"]
        if level not in valid_levels:
            raise ValueError(f"Недопустимый уровень: {level}. Допустимые: {valid_levels}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Обновить уровень и сбросить прогресс
            cursor.execute("""
                UPDATE users 
                SET level = ?,
                    current_day = 1,
                    theme_order = 1,
                    task_in_day = 1,
                    current_theme = NULL
                WHERE user_id = ?
            """, (level, user_id))
            
            if cursor.rowcount == 0:
                logger.warning(f"Пользователь {user_id} не найден для обновления уровня")
                return False
            
            conn.commit()
            logger.info(f"✅ Уровень пользователя {user_id} изменен на {level}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при обновлении уровня пользователя {user_id}: {e}")
            raise
        finally:
            conn.close()
    
    def update_user_progress(
        self, 
        user_id: int, 
        current_day: int = None,
        current_theme: str = None,
        theme_order: int = None,
        task_in_day: int = None
    ) -> bool:
        """
        Обновить прогресс пользователя.
        
        Args:
            user_id: Telegram ID пользователя
            current_day: Текущий день цикла (1-5)
            current_theme: Название текущей темы
            theme_order: Порядковый номер темы
            task_in_day: Номер задания в дне (1-3)
            
        Returns:
            True если обновление успешно, False если пользователь не найден
            
        Raises:
            ValueError: Если значения вне допустимого диапазона
            
        Example:
            >>> db = DatabaseManager()
            >>> db.update_user_progress(123456789, current_day=2, task_in_day=1)
            True
        """
        # Валидация
        if current_day is not None and (current_day < 1 or current_day > 5):
            raise ValueError(f"current_day должен быть от 1 до 5, получено: {current_day}")
        if task_in_day is not None and (task_in_day < 1 or task_in_day > 3):
            raise ValueError(f"task_in_day должен быть от 1 до 3, получено: {task_in_day}")
        if theme_order is not None and theme_order < 1:
            raise ValueError(f"theme_order должен быть >= 1, получено: {theme_order}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Построить динамический запрос только с переданными параметрами
            update_fields = []
            values = []
            
            if current_day is not None:
                update_fields.append("current_day = ?")
                values.append(current_day)
            if current_theme is not None:
                update_fields.append("current_theme = ?")
                values.append(current_theme)
            if theme_order is not None:
                update_fields.append("theme_order = ?")
                values.append(theme_order)
            if task_in_day is not None:
                update_fields.append("task_in_day = ?")
                values.append(task_in_day)
            
            # Всегда обновляем last_task_date
            update_fields.append("last_task_date = CURRENT_DATE")
            
            if not update_fields:
                logger.warning("Нет полей для обновления")
                return False
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
            
            cursor.execute(query, values)
            
            if cursor.rowcount == 0:
                logger.warning(f"Пользователь {user_id} не найден для обновления прогресса")
                return False
            
            conn.commit()
            logger.info(f"✅ Прогресс пользователя {user_id} обновлен")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при обновлении прогресса пользователя {user_id}: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> Optional[dict]:
        """
        Получить статистику пользователя.
        
        Args:
            user_id: Telegram ID пользователя
            
        Returns:
            Словарь со статистикой или None если пользователь не найден
            
        Example:
            >>> db = DatabaseManager()
            >>> stats = db.get_user_stats(123456789)
            >>> print(f"Точность: {stats['accuracy']}%")
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Получить базовую информацию о пользователе
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                logger.info(f"Пользователь {user_id} не найден")
                return None
            
            # Получить статистику из user_progress
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_tasks,
                    SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as incorrect_tasks,
                    SUM(CASE WHEN is_correct IS NULL THEN 1 ELSE 0 END) as unchecked_tasks
                FROM user_progress
                WHERE user_id = ?
            """, (user_id,))
            
            progress_stats = cursor.fetchone()
            
            # Подсчитать процент правильных ответов
            total = progress_stats['total_tasks'] or 0
            correct = progress_stats['correct_tasks'] or 0
            accuracy = round((correct / total * 100), 2) if total > 0 else 0.0
            
            # Получить количество непроверенных открытых вопросов
            cursor.execute("""
                SELECT COUNT(*) as unchecked_answers
                FROM user_answers
                WHERE user_id = ? AND checked = 0
            """, (user_id,))
            
            unchecked = cursor.fetchone()['unchecked_answers']
            
            # Сформировать результат
            stats = {
                'user_id': user['user_id'],
                'username': user['username'],
                'level': user['level'],
                'current_day': user['current_day'],
                'current_theme': user['current_theme'],
                'theme_order': user['theme_order'],
                'task_in_day': user['task_in_day'],
                'started_at': user['started_at'],
                'last_task_date': user['last_task_date'],
                'total_tasks_completed': total,
                'correct_tasks': correct,
                'incorrect_tasks': progress_stats['incorrect_tasks'] or 0,
                'unchecked_tasks': progress_stats['unchecked_tasks'] or 0,
                'accuracy': accuracy,
                'unchecked_open_answers': unchecked
            }
            
            return stats
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при получении статистики пользователя {user_id}: {e}")
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

