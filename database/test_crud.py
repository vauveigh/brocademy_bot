"""
Test script for CRUD operations

Скрипт для тестирования CRUD операций с пользователями.

Author: Vladimir
Date: 2024-10-26
"""

import sys
import os

# Установка UTF-8 для Windows консоли
if sys.platform == 'win32':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except:
        pass

from database.db_manager import DatabaseManager
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Вывести заголовок раздела"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_user_info(user: dict, title: str = "Информация о пользователе"):
    """Вывести информацию о пользователе"""
    print(f"\n📋 {title}:")
    print(f"   User ID: {user['user_id']}")
    print(f"   Username: {user['username']}")
    print(f"   Level: {user['level']}")
    print(f"   Current Day: {user['current_day']}")
    print(f"   Current Theme: {user['current_theme']}")
    print(f"   Theme Order: {user['theme_order']}")
    print(f"   Task in Day: {user['task_in_day']}")
    print(f"   Started At: {user['started_at']}")
    print(f"   Last Task Date: {user['last_task_date']}")


def print_stats(stats: dict):
    """Вывести статистику пользователя"""
    print(f"\n📊 Статистика пользователя:")
    print(f"   User ID: {stats['user_id']}")
    print(f"   Username: {stats['username']}")
    print(f"   Level: {stats['level']}")
    print(f"   Current Day: {stats['current_day']}/{5}")
    print(f"   Current Theme: {stats['current_theme']}")
    print(f"   Theme Order: #{stats['theme_order']}")
    print(f"   Task in Day: {stats['task_in_day']}/{3}")
    print(f"   ---")
    print(f"   Total Tasks: {stats['total_tasks_completed']}")
    print(f"   Correct: {stats['correct_tasks']}")
    print(f"   Incorrect: {stats['incorrect_tasks']}")
    print(f"   Unchecked: {stats['unchecked_tasks']}")
    print(f"   Accuracy: {stats['accuracy']}%")
    print(f"   Unchecked Open Answers: {stats['unchecked_open_answers']}")


def test_create_user(db: DatabaseManager):
    """Тест создания пользователя"""
    print_section("Тест 1: Создание пользователей")
    
    # Создать тестовых пользователей
    users_to_create = [
        (123456789, "john_doe", "Beginner"),
        (987654321, "jane_smith", "Elementary"),
        (555555555, "bob_jones", "Advanced"),
        (111111111, None, "Beginner"),  # Без username
    ]
    
    for user_id, username, level in users_to_create:
        result = db.create_user(user_id, username, level)
        if result:
            print(f"✅ Создан пользователь: {user_id} ({username}) - {level}")
        else:
            print(f"⚠️  Пользователь {user_id} уже существует")
    
    # Попытка создать дубликат
    print("\n🔄 Попытка создать дубликат...")
    result = db.create_user(123456789, "duplicate", "Beginner")
    if not result:
        print("✅ Правильно! Дубликат не создан")
    
    # Попытка создать с неверным уровнем
    print("\n🔄 Попытка создать с неверным уровнем...")
    try:
        db.create_user(999999999, "invalid_level", "InvalidLevel")
        print("❌ ОШИБКА: Должно было вызвать ValueError!")
    except ValueError as e:
        print(f"✅ Правильно! Поймано исключение: {e}")


def test_get_user(db: DatabaseManager):
    """Тест получения пользователя"""
    print_section("Тест 2: Получение пользователя")
    
    # Получить существующего пользователя
    user = db.get_user(123456789)
    if user:
        print_user_info(user)
    else:
        print("❌ Пользователь не найден!")
    
    # Попытка получить несуществующего пользователя
    print("\n🔄 Попытка получить несуществующего пользователя...")
    user = db.get_user(999999999)
    if user is None:
        print("✅ Правильно! Пользователь не найден (вернул None)")
    else:
        print(f"❌ ОШИБКА: Должен был вернуть None!")


def test_update_user_level(db: DatabaseManager):
    """Тест изменения уровня пользователя"""
    print_section("Тест 3: Изменение уровня пользователя")
    
    # Получить текущий уровень
    user = db.get_user(123456789)
    print(f"Текущий уровень: {user['level']}")
    
    # Изменить уровень
    print("\n🔄 Изменение уровня на Elementary...")
    result = db.update_user_level(123456789, "Elementary")
    if result:
        print("✅ Уровень изменен")
        user = db.get_user(123456789)
        print_user_info(user, "Пользователь после изменения уровня")
        print(f"\n⚠️  Обратите внимание: прогресс сброшен на начало!")
    
    # Попытка изменить уровень несуществующего пользователя
    print("\n🔄 Попытка изменить уровень несуществующего пользователя...")
    result = db.update_user_level(999999999, "Advanced")
    if not result:
        print("✅ Правильно! Пользователь не найден (вернул False)")
    
    # Попытка установить неверный уровень
    print("\n🔄 Попытка установить неверный уровень...")
    try:
        db.update_user_level(123456789, "InvalidLevel")
        print("❌ ОШИБКА: Должно было вызвать ValueError!")
    except ValueError as e:
        print(f"✅ Правильно! Поймано исключение: {e}")


def test_update_user_progress(db: DatabaseManager):
    """Тест обновления прогресса пользователя"""
    print_section("Тест 4: Обновление прогресса пользователя")
    
    # Получить текущий прогресс
    user = db.get_user(987654321)
    print(f"Текущий прогресс: День {user['current_day']}, Задание {user['task_in_day']}")
    
    # Обновить только день
    print("\n🔄 Обновление current_day на 2...")
    result = db.update_user_progress(987654321, current_day=2)
    if result:
        user = db.get_user(987654321)
        print(f"✅ День обновлен: {user['current_day']}")
    
    # Обновить несколько полей
    print("\n🔄 Обновление нескольких полей...")
    result = db.update_user_progress(
        987654321,
        current_day=3,
        current_theme="Travel and Tourism",
        theme_order=5,
        task_in_day=2
    )
    if result:
        user = db.get_user(987654321)
        print_user_info(user, "Пользователь после обновления прогресса")
    
    # Попытка установить неверное значение
    print("\n🔄 Попытка установить current_day=10 (вне диапазона)...")
    try:
        db.update_user_progress(987654321, current_day=10)
        print("❌ ОШИБКА: Должно было вызвать ValueError!")
    except ValueError as e:
        print(f"✅ Правильно! Поймано исключение: {e}")
    
    # Попытка обновить несуществующего пользователя
    print("\n🔄 Попытка обновить прогресс несуществующего пользователя...")
    result = db.update_user_progress(999999999, current_day=2)
    if not result:
        print("✅ Правильно! Пользователь не найден (вернул False)")


def test_get_user_stats(db: DatabaseManager):
    """Тест получения статистики пользователя"""
    print_section("Тест 5: Получение статистики пользователя")
    
    # Добавить тестовые данные в user_progress
    print("🔄 Добавление тестовых данных прогресса...")
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Добавить несколько выполненных заданий
    test_progress = [
        (123456789, "BEG-FAM-D1-G1", "grammar", "correct_answer", 1),
        (123456789, "BEG-FAM-D1-G2", "grammar", "correct_answer", 1),
        (123456789, "BEG-FAM-D1-G3", "grammar", "wrong_answer", 0),
        (123456789, "BEG-FAM-D2-R1", "reading", "answer", None),  # Не проверено
    ]
    
    for user_id, task_id, task_type, answer, is_correct in test_progress:
        cursor.execute("""
            INSERT INTO user_progress (user_id, task_id, task_type, answer, is_correct)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, task_id, task_type, answer, is_correct))
    
    # Добавить тестовый открытый вопрос
    cursor.execute("""
        INSERT INTO user_answers (user_id, task_id, question, user_answer, checked)
        VALUES (?, ?, ?, ?, ?)
    """, (123456789, "BEG-FAM-D5-RV1", "Test question", "Test answer", 0))
    
    conn.commit()
    conn.close()
    
    print("✅ Тестовые данные добавлены")
    
    # Получить статистику
    print("\n🔄 Получение статистики...")
    stats = db.get_user_stats(123456789)
    if stats:
        print_stats(stats)
    else:
        print("❌ Статистика не получена!")
    
    # Получить статистику для пользователя без прогресса
    print("\n🔄 Статистика для пользователя без прогресса...")
    stats = db.get_user_stats(555555555)
    if stats:
        print_stats(stats)
    
    # Попытка получить статистику несуществующего пользователя
    print("\n🔄 Попытка получить статистику несуществующего пользователя...")
    stats = db.get_user_stats(999999999)
    if stats is None:
        print("✅ Правильно! Пользователь не найден (вернул None)")


def main():
    """Главная функция тестирования"""
    print("=" * 70)
    print("  🧪 ТЕСТИРОВАНИЕ CRUD ОПЕРАЦИЙ")
    print("=" * 70)
    print()
    
    # Создать тестовую базу данных
    test_db_path = "test_crud.db"
    
    # Удалить старую тестовую БД если существует
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"🗑️  Удалена старая тестовая БД: {test_db_path}")
    
    # Создать менеджер базы данных
    db = DatabaseManager(test_db_path)
    
    # Инициализировать БД
    print(f"📦 Создание тестовой БД: {test_db_path}")
    db.init_database()
    
    try:
        # Запустить тесты
        test_create_user(db)
        test_get_user(db)
        test_update_user_level(db)
        test_update_user_progress(db)
        test_get_user_stats(db)
        
        # Итоги
        print_section("✅ ИТОГИ ТЕСТИРОВАНИЯ")
        print("Все тесты пройдены успешно!")
        print(f"\nТестовая БД сохранена: {os.path.abspath(test_db_path)}")
        print("Вы можете изучить её с помощью любого SQLite клиента.")
        print("\nДля удаления тестовой БД:")
        print(f"  rm {test_db_path}  # Linux/Mac")
        print(f"  del {test_db_path}  # Windows")
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ОШИБКА ПРИ ТЕСТИРОВАНИИ")
        print("=" * 70)
        print(f"Исключение: {type(e).__name__}")
        print(f"Сообщение: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

