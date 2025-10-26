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
    
    # ==================== Работа с прогрессом ====================
    
    def save_task_answer(
        self,
        user_id: int,
        task_id: str,
        task_type: str,
        answer: str,
        is_correct: Optional[bool] = None
    ) -> bool:
        """
        Сохранить ответ пользователя на задание.
        
        Args:
            user_id: Telegram ID пользователя
            task_id: ID задания из Notion
            task_type: Тип задания (grammar/reading/vocabulary/situations/review)
            answer: Ответ пользователя
            is_correct: Правильность ответа (None для open_question)
            
        Returns:
            True если ответ сохранен успешно
            
        Raises:
            ValueError: Если task_type недопустим
            sqlite3.Error: При ошибке БД
            
        Example:
            >>> db = DatabaseManager()
            >>> db.save_task_answer(123456789, "BEG-FAM-D1-G1", "grammar", "my", True)
            True
        """
        # Валидация типа задания
        valid_types = ["grammar", "reading", "vocabulary", "situations", "review"]
        if task_type not in valid_types:
            raise ValueError(f"Недопустимый тип задания: {task_type}. Допустимые: {valid_types}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Сохранить ответ в user_progress
            cursor.execute("""
                INSERT INTO user_progress (user_id, task_id, task_type, answer, is_correct)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, task_id, task_type, answer, is_correct))
            
            conn.commit()
            
            correct_status = "✅" if is_correct else "❌" if is_correct is False else "⏳"
            logger.info(f"{correct_status} Сохранен ответ пользователя {user_id} на задание {task_id}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при сохранении ответа пользователя {user_id}: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_progress_stats(self, user_id: int) -> Optional[dict]:
        """
        Получить статистику прогресса пользователя (только процент правильных ответов).
        
        Args:
            user_id: Telegram ID пользователя
            
        Returns:
            Словарь со статистикой или None если пользователь не найден
            
        Example:
            >>> db = DatabaseManager()
            >>> stats = db.get_user_progress_stats(123456789)
            >>> print(f"Точность: {stats['accuracy']}%")
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Проверить существование пользователя
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                logger.info(f"Пользователь {user_id} не найден")
                return None
            
            # Получить статистику по типам заданий
            cursor.execute("""
                SELECT 
                    task_type,
                    COUNT(*) as total,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                    SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as incorrect,
                    SUM(CASE WHEN is_correct IS NULL THEN 1 ELSE 0 END) as unchecked
                FROM user_progress
                WHERE user_id = ?
                GROUP BY task_type
            """, (user_id,))
            
            stats_by_type = {}
            for row in cursor.fetchall():
                task_type = row['task_type']
                total = row['total']
                correct = row['correct']
                
                accuracy = round((correct / total * 100), 2) if total > 0 else 0.0
                
                stats_by_type[task_type] = {
                    'total': total,
                    'correct': correct,
                    'incorrect': row['incorrect'],
                    'unchecked': row['unchecked'],
                    'accuracy': accuracy
                }
            
            # Общая статистика
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                    SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as incorrect,
                    SUM(CASE WHEN is_correct IS NULL THEN 1 ELSE 0 END) as unchecked
                FROM user_progress
                WHERE user_id = ?
            """, (user_id,))
            
            overall = cursor.fetchone()
            total = overall['total'] or 0
            correct = overall['correct'] or 0
            
            overall_accuracy = round((correct / total * 100), 2) if total > 0 else 0.0
            
            return {
                'user_id': user_id,
                'total_tasks': total,
                'correct_tasks': correct,
                'incorrect_tasks': overall['incorrect'] or 0,
                'unchecked_tasks': overall['unchecked'] or 0,
                'accuracy': overall_accuracy,
                'by_type': stats_by_type
            }
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при получении статистики прогресса {user_id}: {e}")
            raise
        finally:
            conn.close()
    
    def get_completed_tasks_count(self, user_id: int) -> int:
        """
        Получить количество выполненных заданий пользователя.
        
        Args:
            user_id: Telegram ID пользователя
            
        Returns:
            Количество выполненных заданий
            
        Example:
            >>> db = DatabaseManager()
            >>> count = db.get_completed_tasks_count(123456789)
            >>> print(f"Выполнено заданий: {count}")
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM user_progress
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            count = result['count'] if result else 0
            
            return count
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при подсчете заданий пользователя {user_id}: {e}")
            raise
        finally:
            conn.close()
    
    def get_current_day_progress(self, user_id: int) -> Optional[dict]:
        """
        Получить прогресс выполнения заданий за текущий день.
        
        Args:
            user_id: Telegram ID пользователя
            
        Returns:
            Словарь с информацией о прогрессе или None если пользователь не найден
            
        Example:
            >>> db = DatabaseManager()
            >>> progress = db.get_current_day_progress(123456789)
            >>> print(f"Выполнено сегодня: {progress['completed_today']}/3")
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Получить информацию о пользователе
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                logger.info(f"Пользователь {user_id} не найден")
                return None
            
            # Подсчитать задания выполненные сегодня
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM user_progress
                WHERE user_id = ? AND DATE(answered_at) = CURRENT_DATE
            """, (user_id,))
            
            result = cursor.fetchone()
            completed_today = result['count'] if result else 0
            
            return {
                'user_id': user_id,
                'current_day': user['current_day'],
                'current_theme': user['current_theme'],
                'theme_order': user['theme_order'],
                'task_in_day': user['task_in_day'],
                'completed_today': completed_today,
                'remaining_today': max(0, 3 - completed_today),
                'last_task_date': user['last_task_date']
            }
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при получении прогресса дня для {user_id}: {e}")
            raise
        finally:
            conn.close()
    
    def advance_to_next_task(self, user_id: int) -> Optional[dict]:
        """
        Переход к следующему заданию с автоматической логикой переходов между днями и темами.
        
        Логика:
        - Если task_in_day < 3: переход к следующему заданию в дне
        - Если task_in_day = 3 и current_day < 5: переход к следующему дню
        - Если task_in_day = 3 и current_day = 5: переход к новой теме
        
        Args:
            user_id: Telegram ID пользователя
            
        Returns:
            Словарь с новым состоянием или None если пользователь не найден
            
        Example:
            >>> db = DatabaseManager()
            >>> new_state = db.advance_to_next_task(123456789)
            >>> print(f"Новое состояние: День {new_state['current_day']}, Задание {new_state['task_in_day']}")
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Получить текущее состояние пользователя
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                logger.info(f"Пользователь {user_id} не найден")
                return None
            
            current_day = user['current_day']
            current_theme = user['current_theme']
            theme_order = user['theme_order']
            task_in_day = user['task_in_day']
            
            # Определить новое состояние
            new_day = current_day
            new_theme_order = theme_order
            new_task = task_in_day
            transition_type = None
            
            if task_in_day < 3:
                # Следующее задание в текущем дне
                new_task = task_in_day + 1
                transition_type = "next_task"
                logger.info(f"Пользователь {user_id}: переход к заданию {new_task}/3 в дне {current_day}")
                
            elif task_in_day == 3 and current_day < 5:
                # Следующий день
                new_day = current_day + 1
                new_task = 1
                transition_type = "next_day"
                logger.info(f"Пользователь {user_id}: переход к дню {new_day}/5")
                
            elif task_in_day == 3 and current_day == 5:
                # Новая тема
                new_day = 1
                new_task = 1
                new_theme_order = theme_order + 1
                transition_type = "next_theme"
                logger.info(f"Пользователь {user_id}: переход к новой теме (порядок {new_theme_order})")
            
            # Обновить состояние в БД
            cursor.execute("""
                UPDATE users
                SET current_day = ?,
                    theme_order = ?,
                    task_in_day = ?,
                    last_task_date = CURRENT_DATE
                WHERE user_id = ?
            """, (new_day, new_theme_order, new_task, user_id))
            
            # Если переход на новую тему, сбросить current_theme (будет установлена при загрузке из Notion)
            if transition_type == "next_theme":
                cursor.execute("""
                    UPDATE users
                    SET current_theme = NULL
                    WHERE user_id = ?
                """, (user_id,))
            
            conn.commit()
            
            logger.info(f"✅ Пользователь {user_id}: переход выполнен ({transition_type})")
            
            return {
                'user_id': user_id,
                'previous_state': {
                    'day': current_day,
                    'theme_order': theme_order,
                    'task': task_in_day
                },
                'new_state': {
                    'day': new_day,
                    'theme_order': new_theme_order,
                    'task': new_task
                },
                'transition_type': transition_type,
                'message': self._get_transition_message(transition_type, new_day, new_theme_order)
            }
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при переходе к следующему заданию для {user_id}: {e}")
            raise
        finally:
            conn.close()
    
    def _get_transition_message(self, transition_type: str, new_day: int, new_theme_order: int) -> str:
        """
        Получить сообщение о переходе для пользователя.
        
        Args:
            transition_type: Тип перехода (next_task/next_day/next_theme)
            new_day: Новый день
            new_theme_order: Новый порядковый номер темы
            
        Returns:
            Строка с сообщением
        """
        if transition_type == "next_task":
            return f"Переходим к следующему заданию!"
        elif transition_type == "next_day":
            day_names = {
                1: "Grammar (Грамматика)",
                2: "Reading (Чтение)",
                3: "Vocabulary (Словарный запас)",
                4: "Situations (Жизненные ситуации)",
                5: "Review (Повторение)"
            }
            return f"🎉 День завершен! Переходим к дню {new_day}: {day_names.get(new_day, 'Новый день')}"
        elif transition_type == "next_theme":
            return f"🎊 Тема завершена! Переходим к новой теме (#{new_theme_order})"
        return "Переход выполнен"
    
    # ==================== Открытые вопросы ====================
    
    def save_open_answer(
        self,
        user_id: int,
        task_id: str,
        question: str,
        user_answer: str
    ) -> bool:
        """
        Сохранить ответ на открытый вопрос для проверки преподавателем.
        
        Args:
            user_id: Telegram ID пользователя
            task_id: ID задания из Notion
            question: Текст вопроса
            user_answer: Ответ пользователя
            
        Returns:
            True если ответ сохранен успешно
            
        Raises:
            sqlite3.Error: При ошибке БД
            
        Example:
            >>> db = DatabaseManager()
            >>> db.save_open_answer(
            ...     123456789,
            ...     "BEG-FAM-D5-RV1",
            ...     "Describe your family.",
            ...     "My family is small and friendly."
            ... )
            True
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Сохранить ответ в user_answers
            cursor.execute("""
                INSERT INTO user_answers (user_id, task_id, question, user_answer, checked)
                VALUES (?, ?, ?, ?, 0)
            """, (user_id, task_id, question, user_answer))
            
            conn.commit()
            
            logger.info(f"📝 Сохранен открытый ответ пользователя {user_id} на задание {task_id}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при сохранении открытого ответа {user_id}: {e}")
            raise
        finally:
            conn.close()
    
    def get_unchecked_answers(self, limit: Optional[int] = None) -> list:
        """
        Получить список непроверенных открытых ответов для веб-интерфейса.
        
        Args:
            limit: Максимальное количество ответов (None = все)
            
        Returns:
            Список словарей с непроверенными ответами
            
        Example:
            >>> db = DatabaseManager()
            >>> answers = db.get_unchecked_answers(limit=10)
            >>> for answer in answers:
            ...     print(f"User: {answer['user_id']}, Question: {answer['question']}")
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT 
                    ua.id,
                    ua.user_id,
                    ua.task_id,
                    ua.question,
                    ua.user_answer,
                    ua.created_at,
                    u.username,
                    u.level
                FROM user_answers ua
                LEFT JOIN users u ON ua.user_id = u.user_id
                WHERE ua.checked = 0
                ORDER BY ua.created_at ASC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            answers = []
            for row in rows:
                answers.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'username': row['username'],
                    'level': row['level'],
                    'task_id': row['task_id'],
                    'question': row['question'],
                    'user_answer': row['user_answer'],
                    'created_at': row['created_at']
                })
            
            logger.info(f"📋 Получено {len(answers)} непроверенных ответов")
            return answers
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при получении непроверенных ответов: {e}")
            raise
        finally:
            conn.close()
    
    def mark_answer_as_checked(self, answer_id: int) -> bool:
        """
        Пометить открытый ответ как проверенный преподавателем.
        
        Args:
            answer_id: ID ответа в таблице user_answers
            
        Returns:
            True если ответ помечен, False если ответ не найден
            
        Example:
            >>> db = DatabaseManager()
            >>> db.mark_answer_as_checked(42)
            True
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE user_answers
                SET checked = 1
                WHERE id = ?
            """, (answer_id,))
            
            if cursor.rowcount == 0:
                logger.warning(f"Ответ с ID {answer_id} не найден")
                return False
            
            conn.commit()
            logger.info(f"✅ Ответ {answer_id} помечен как проверенный")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при пометке ответа {answer_id}: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_open_answers(
        self,
        user_id: int,
        checked: Optional[bool] = None
    ) -> list:
        """
        Получить все открытые ответы конкретного пользователя.
        
        Args:
            user_id: Telegram ID пользователя
            checked: Фильтр по статусу (True/False/None=все)
            
        Returns:
            Список словарей с ответами пользователя
            
        Example:
            >>> db = DatabaseManager()
            >>> # Все непроверенные ответы пользователя
            >>> unchecked = db.get_user_open_answers(123456789, checked=False)
            >>> # Все ответы пользователя
            >>> all_answers = db.get_user_open_answers(123456789)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT 
                    id,
                    user_id,
                    task_id,
                    question,
                    user_answer,
                    created_at,
                    checked
                FROM user_answers
                WHERE user_id = ?
            """
            
            params = [user_id]
            
            if checked is not None:
                query += " AND checked = ?"
                params.append(1 if checked else 0)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            answers = []
            for row in rows:
                answers.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'task_id': row['task_id'],
                    'question': row['question'],
                    'user_answer': row['user_answer'],
                    'created_at': row['created_at'],
                    'checked': bool(row['checked'])
                })
            
            logger.info(f"📋 Получено {len(answers)} ответов пользователя {user_id}")
            return answers
            
        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка при получении ответов пользователя {user_id}: {e}")
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

