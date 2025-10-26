"""
Test script for progress operations

Скрипт для тестирования операций работы с прогрессом пользователей.

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


def test_save_task_answer(db: DatabaseManager):
    """Тест сохранения ответов на задания"""
    print_section("Тест 1: Сохранение ответов на задания")
    
    user_id = 123456789
    
    # Сохранить правильные ответы
    print("🔄 Сохранение правильных ответов на Grammar...")
    answers = [
        ("BEG-FAM-D1-G1", "grammar", "my", True),
        ("BEG-FAM-D1-G2", "grammar", "is", True),
        ("BEG-FAM-D1-G3", "grammar", "are", False),  # Неправильный
    ]
    
    for task_id, task_type, answer, is_correct in answers:
        result = db.save_task_answer(user_id, task_id, task_type, answer, is_correct)
        if result:
            status = "✅" if is_correct else "❌"
            print(f"{status} Ответ сохранен: {task_id}")
    
    # Сохранить ответы на Reading
    print("\n🔄 Сохранение ответов на Reading...")
    reading_answers = [
        ("BEG-FAM-D2-R1", "reading", "answer A", True),
        ("BEG-FAM-D2-R2", "reading", "answer B", True),
    ]
    
    for task_id, task_type, answer, is_correct in reading_answers:
        db.save_task_answer(user_id, task_id, task_type, answer, is_correct)
        print(f"✅ Ответ сохранен: {task_id}")
    
    # Сохранить открытый вопрос (не проверено)
    print("\n🔄 Сохранение открытого вопроса...")
    result = db.save_task_answer(
        user_id,
        "BEG-FAM-D5-RV1",
        "review",
        "My family is very friendly and supportive.",
        None  # Не проверено
    )
    if result:
        print("⏳ Открытый вопрос сохранен (ожидает проверки)")
    
    # Попытка сохранить с неверным типом задания
    print("\n🔄 Попытка сохранить с неверным типом задания...")
    try:
        db.save_task_answer(user_id, "TEST-ID", "invalid_type", "answer", True)
        print("❌ ОШИБКА: Должно было вызвать ValueError!")
    except ValueError as e:
        print(f"✅ Правильно! Поймано исключение: {e}")


def test_get_user_progress_stats(db: DatabaseManager):
    """Тест получения статистики прогресса"""
    print_section("Тест 2: Получение статистики прогресса")
    
    user_id = 123456789
    
    print("🔄 Получение статистики...")
    stats = db.get_user_progress_stats(user_id)
    
    if stats:
        print("\n📊 Общая статистика:")
        print(f"   Всего заданий: {stats['total_tasks']}")
        print(f"   Правильно: {stats['correct_tasks']}")
        print(f"   Неправильно: {stats['incorrect_tasks']}")
        print(f"   Не проверено: {stats['unchecked_tasks']}")
        print(f"   Точность: {stats['accuracy']}%")
        
        if stats['by_type']:
            print("\n📊 Статистика по типам заданий:")
            for task_type, type_stats in stats['by_type'].items():
                print(f"\n   {task_type.upper()}:")
                print(f"      Всего: {type_stats['total']}")
                print(f"      Правильно: {type_stats['correct']}")
                print(f"      Точность: {type_stats['accuracy']}%")
    
    # Статистика для пользователя без ответов
    print("\n🔄 Статистика для пользователя без ответов...")
    user_id_no_progress = 987654321
    stats = db.get_user_progress_stats(user_id_no_progress)
    if stats:
        print(f"✅ Получена статистика: {stats['total_tasks']} заданий")
    
    # Статистика для несуществующего пользователя
    print("\n🔄 Статистика для несуществующего пользователя...")
    stats = db.get_user_progress_stats(999999999)
    if stats is None:
        print("✅ Правильно! Пользователь не найден (вернул None)")


def test_get_completed_tasks_count(db: DatabaseManager):
    """Тест подсчета выполненных заданий"""
    print_section("Тест 3: Подсчет выполненных заданий")
    
    user_id = 123456789
    
    print("🔄 Подсчет заданий...")
    count = db.get_completed_tasks_count(user_id)
    print(f"✅ Пользователь {user_id} выполнил {count} заданий")
    
    # Подсчет для пользователя без заданий
    user_id_no_tasks = 555555555
    count = db.get_completed_tasks_count(user_id_no_tasks)
    print(f"✅ Пользователь {user_id_no_tasks} выполнил {count} заданий")


def test_get_current_day_progress(db: DatabaseManager):
    """Тест получения прогресса текущего дня"""
    print_section("Тест 4: Прогресс текущего дня")
    
    user_id = 123456789
    
    print("🔄 Получение прогресса дня...")
    progress = db.get_current_day_progress(user_id)
    
    if progress:
        print("\n📊 Прогресс текущего дня:")
        print(f"   User ID: {progress['user_id']}")
        print(f"   Текущий день: {progress['current_day']}/5")
        print(f"   Текущая тема: {progress['current_theme']}")
        print(f"   Порядок темы: #{progress['theme_order']}")
        print(f"   Задание в дне: {progress['task_in_day']}/3")
        print(f"   Выполнено сегодня: {progress['completed_today']}")
        print(f"   Осталось сегодня: {progress['remaining_today']}")
        print(f"   Последнее задание: {progress['last_task_date']}")
    
    # Прогресс для несуществующего пользователя
    print("\n🔄 Прогресс для несуществующего пользователя...")
    progress = db.get_current_day_progress(999999999)
    if progress is None:
        print("✅ Правильно! Пользователь не найден (вернул None)")


def test_advance_to_next_task(db: DatabaseManager):
    """Тест логики переходов между заданиями, днями и темами"""
    print_section("Тест 5: Переходы между заданиями, днями и темами")
    
    # Создать нового пользователя для тестирования переходов
    test_user_id = 111111111
    db.create_user(test_user_id, "test_user", "Beginner")
    print(f"✅ Создан тестовый пользователь {test_user_id}")
    
    # Тест 1: Переход к следующему заданию в текущем дне
    print("\n🔄 Тест 1: Переход к заданию 2 (в текущем дне)")
    result = db.advance_to_next_task(test_user_id)
    if result:
        print(f"   Тип перехода: {result['transition_type']}")
        print(f"   Было: День {result['previous_state']['day']}, Задание {result['previous_state']['task']}")
        print(f"   Стало: День {result['new_state']['day']}, Задание {result['new_state']['task']}")
        print(f"   Сообщение: {result['message']}")
        
        if result['transition_type'] == 'next_task' and result['new_state']['task'] == 2:
            print("   ✅ Правильно! Переход к заданию 2")
    
    # Тест 2: Переход к заданию 3
    print("\n🔄 Тест 2: Переход к заданию 3 (в текущем дне)")
    result = db.advance_to_next_task(test_user_id)
    if result:
        print(f"   Тип перехода: {result['transition_type']}")
        print(f"   Стало: День {result['new_state']['day']}, Задание {result['new_state']['task']}")
        
        if result['transition_type'] == 'next_task' and result['new_state']['task'] == 3:
            print("   ✅ Правильно! Переход к заданию 3")
    
    # Тест 3: Переход к следующему дню
    print("\n🔄 Тест 3: Переход к дню 2 (новый день)")
    result = db.advance_to_next_task(test_user_id)
    if result:
        print(f"   Тип перехода: {result['transition_type']}")
        print(f"   Было: День {result['previous_state']['day']}, Задание {result['previous_state']['task']}")
        print(f"   Стало: День {result['new_state']['day']}, Задание {result['new_state']['task']}")
        print(f"   Сообщение: {result['message']}")
        
        if result['transition_type'] == 'next_day' and result['new_state']['day'] == 2:
            print("   ✅ Правильно! Переход к дню 2")
    
    # Тест 4: Быстрая прокрутка до конца темы
    print("\n🔄 Тест 4: Быстрая прокрутка до конца темы...")
    
    # Установить состояние: День 5, Задание 3 (последнее задание темы)
    db.update_user_progress(test_user_id, current_day=5, task_in_day=3)
    print("   Установлено: День 5, Задание 3")
    
    # Переход к новой теме
    print("\n🔄 Переход к новой теме...")
    result = db.advance_to_next_task(test_user_id)
    if result:
        print(f"   Тип перехода: {result['transition_type']}")
        print(f"   Было: День {result['previous_state']['day']}, Задание {result['previous_state']['task']}, Тема #{result['previous_state']['theme_order']}")
        print(f"   Стало: День {result['new_state']['day']}, Задание {result['new_state']['task']}, Тема #{result['new_state']['theme_order']}")
        print(f"   Сообщение: {result['message']}")
        
        if (result['transition_type'] == 'next_theme' and 
            result['new_state']['day'] == 1 and 
            result['new_state']['task'] == 1 and
            result['new_state']['theme_order'] == 2):
            print("   ✅ Правильно! Переход к новой теме (тема #2)")
    
    # Тест 5: Попытка перехода для несуществующего пользователя
    print("\n🔄 Тест 5: Переход для несуществующего пользователя...")
    result = db.advance_to_next_task(999999999)
    if result is None:
        print("✅ Правильно! Пользователь не найден (вернул None)")


def test_full_cycle(db: DatabaseManager):
    """Тест полного цикла: ответ на задание -> переход к следующему"""
    print_section("Тест 6: Полный цикл (ответ + переход)")
    
    # Создать нового пользователя
    cycle_user_id = 222222222
    db.create_user(cycle_user_id, "cycle_test", "Elementary")
    print(f"✅ Создан тестовый пользователь {cycle_user_id}")
    
    # Симуляция выполнения 9 заданий (3 дня по 3 задания)
    day_types = {
        1: "grammar",
        2: "reading",
        3: "vocabulary"
    }
    
    for day in range(1, 4):
        print(f"\n📅 День {day} ({day_types[day].upper()}):")
        
        for task_num in range(1, 4):
            # Получить текущий прогресс
            progress = db.get_current_day_progress(cycle_user_id)
            current_day = progress['current_day']
            current_task = progress['task_in_day']
            
            # Сохранить ответ
            task_id = f"EL-TEST-D{current_day}-T{current_task}"
            task_type = day_types[current_day]
            answer = f"answer_{task_num}"
            is_correct = (task_num != 3)  # Третье задание неправильное
            
            db.save_task_answer(cycle_user_id, task_id, task_type, answer, is_correct)
            
            # Переход к следующему заданию
            result = db.advance_to_next_task(cycle_user_id)
            
            status = "✅" if is_correct else "❌"
            print(f"   {status} Задание {task_num}/3 выполнено")
            
            if task_num == 3 and result:
                print(f"   → {result['message']}")
    
    # Показать финальную статистику
    print("\n📊 Финальная статистика:")
    stats = db.get_user_progress_stats(cycle_user_id)
    if stats:
        print(f"   Всего заданий: {stats['total_tasks']}")
        print(f"   Правильно: {stats['correct_tasks']}")
        print(f"   Неправильно: {stats['incorrect_tasks']}")
        print(f"   Точность: {stats['accuracy']}%")
        
        print("\n   По типам:")
        for task_type, type_stats in stats['by_type'].items():
            print(f"      {task_type}: {type_stats['correct']}/{type_stats['total']} ({type_stats['accuracy']}%)")
    
    # Текущее состояние
    user = db.get_user(cycle_user_id)
    print(f"\n📍 Текущая позиция:")
    print(f"   День: {user['current_day']}/5")
    print(f"   Задание: {user['task_in_day']}/3")


def main():
    """Главная функция тестирования"""
    print("=" * 70)
    print("  🧪 ТЕСТИРОВАНИЕ ОПЕРАЦИЙ РАБОТЫ С ПРОГРЕССОМ")
    print("=" * 70)
    print()
    
    # Создать тестовую базу данных
    test_db_path = "test_progress.db"
    
    # Удалить старую тестовую БД если существует
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"🗑️  Удалена старая тестовая БД: {test_db_path}")
    
    # Создать менеджер базы данных
    db = DatabaseManager(test_db_path)
    
    # Инициализировать БД
    print(f"📦 Создание тестовой БД: {test_db_path}")
    db.init_database()
    
    # Создать тестовых пользователей
    print("\n🔄 Создание тестовых пользователей...")
    db.create_user(123456789, "john_doe", "Beginner")
    db.create_user(987654321, "jane_smith", "Elementary")
    db.create_user(555555555, "bob_jones", "Advanced")
    print("✅ Тестовые пользователи созданы")
    
    try:
        # Запустить тесты
        test_save_task_answer(db)
        test_get_user_progress_stats(db)
        test_get_completed_tasks_count(db)
        test_get_current_day_progress(db)
        test_advance_to_next_task(db)
        test_full_cycle(db)
        
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

