"""
Test script for open answer operations

Скрипт для тестирования операций с открытыми вопросами.

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


def print_answer(answer: dict, index: int = None):
    """Вывести информацию об ответе"""
    prefix = f"#{index}" if index else "Ответ"
    checked_status = "✅" if answer.get('checked') else "⏳"
    
    print(f"\n{prefix} {checked_status} ID: {answer['id']}")
    print(f"   User: {answer['user_id']} ({answer.get('username', 'N/A')})")
    if 'level' in answer:
        print(f"   Level: {answer['level']}")
    print(f"   Task: {answer['task_id']}")
    print(f"   Question: {answer['question']}")
    print(f"   Answer: {answer['user_answer']}")
    print(f"   Created: {answer['created_at']}")
    if 'checked' in answer:
        print(f"   Checked: {'Да' if answer['checked'] else 'Нет'}")


def test_save_open_answer(db: DatabaseManager):
    """Тест сохранения открытых ответов"""
    print_section("Тест 1: Сохранение открытых ответов")
    
    # Сохранить несколько открытых ответов от разных пользователей
    test_answers = [
        (123456789, "BEG-FAM-D5-RV1", "Describe your family in 3-4 sentences.", 
         "My family is small. I have a mother, father and sister. We live in Moscow. We are very happy."),
        (123456789, "BEG-FAM-D5-RV2", "What do you like to do with your family?",
         "We like to go to the park together. Sometimes we watch movies at home. I love spending time with them."),
        (987654321, "EL-WORK-D4-S2", "How would you introduce yourself in a job interview?",
         "Hello, my name is Jane. I have 5 years of experience in marketing. I am good at social media and analytics."),
        (987654321, "EL-TRAVEL-D5-RV1", "Describe your dream vacation.",
         "I would like to visit Japan. I want to see Tokyo and Kyoto. I am interested in Japanese culture and food."),
        (555555555, "ADV-BUSINESS-D3-V2", "Explain the difference between B2B and B2C marketing.",
         "B2B focuses on businesses as customers, while B2C targets individual consumers. The strategies and channels differ significantly."),
    ]
    
    print("🔄 Сохранение открытых ответов...")
    for user_id, task_id, question, answer in test_answers:
        result = db.save_open_answer(user_id, task_id, question, answer)
        if result:
            print(f"✅ Ответ сохранен: {task_id} (user {user_id})")
    
    print(f"\n✅ Всего сохранено {len(test_answers)} открытых ответов")


def test_get_unchecked_answers(db: DatabaseManager):
    """Тест получения непроверенных ответов"""
    print_section("Тест 2: Получение непроверенных ответов")
    
    # Получить все непроверенные ответы
    print("🔄 Получение всех непроверенных ответов...")
    answers = db.get_unchecked_answers()
    
    print(f"\n📋 Найдено {len(answers)} непроверенных ответов:")
    for i, answer in enumerate(answers, 1):
        print_answer(answer, i)
    
    # Получить с лимитом
    print("\n🔄 Получение первых 3 непроверенных ответов...")
    limited = db.get_unchecked_answers(limit=3)
    print(f"✅ Получено {len(limited)} ответов с лимитом")
    
    return answers


def test_mark_answer_as_checked(db: DatabaseManager, answers: list):
    """Тест пометки ответов как проверенные"""
    print_section("Тест 3: Пометка ответов как проверенные")
    
    if not answers:
        print("⚠️ Нет ответов для тестирования")
        return
    
    # Пометить первый ответ как проверенный
    first_answer = answers[0]
    print(f"🔄 Пометка ответа {first_answer['id']} как проверенный...")
    result = db.mark_answer_as_checked(first_answer['id'])
    
    if result:
        print(f"✅ Ответ {first_answer['id']} помечен как проверенный")
    
    # Пометить еще два ответа
    if len(answers) >= 3:
        print("\n🔄 Пометка еще двух ответов...")
        for answer in answers[1:3]:
            db.mark_answer_as_checked(answer['id'])
            print(f"✅ Ответ {answer['id']} помечен как проверенный")
    
    # Попытка пометить несуществующий ответ
    print("\n🔄 Попытка пометить несуществующий ответ...")
    result = db.mark_answer_as_checked(999999)
    if not result:
        print("✅ Правильно! Несуществующий ответ не найден")


def test_get_unchecked_after_marking(db: DatabaseManager):
    """Тест получения непроверенных после пометки"""
    print_section("Тест 4: Непроверенные ответы после пометки")
    
    print("🔄 Получение оставшихся непроверенных ответов...")
    answers = db.get_unchecked_answers()
    
    print(f"\n📋 Осталось {len(answers)} непроверенных ответов:")
    for i, answer in enumerate(answers, 1):
        print_answer(answer, i)


def test_get_user_open_answers(db: DatabaseManager):
    """Тест получения ответов конкретного пользователя"""
    print_section("Тест 5: Получение ответов пользователя")
    
    user_id = 123456789
    
    # Все ответы пользователя
    print(f"🔄 Получение всех ответов пользователя {user_id}...")
    all_answers = db.get_user_open_answers(user_id)
    
    print(f"\n📋 Всего ответов пользователя: {len(all_answers)}")
    for i, answer in enumerate(all_answers, 1):
        print_answer(answer, i)
    
    # Только непроверенные
    print(f"\n🔄 Получение непроверенных ответов пользователя {user_id}...")
    unchecked = db.get_user_open_answers(user_id, checked=False)
    print(f"📋 Непроверенных ответов: {len(unchecked)}")
    
    # Только проверенные
    print(f"\n🔄 Получение проверенных ответов пользователя {user_id}...")
    checked = db.get_user_open_answers(user_id, checked=True)
    print(f"📋 Проверенных ответов: {len(checked)}")
    
    # Ответы другого пользователя
    user_id_2 = 987654321
    print(f"\n🔄 Получение ответов пользователя {user_id_2}...")
    user2_answers = db.get_user_open_answers(user_id_2)
    print(f"📋 Ответов пользователя {user_id_2}: {len(user2_answers)}")


def test_workflow_simulation(db: DatabaseManager):
    """Тест полного рабочего процесса"""
    print_section("Тест 6: Симуляция рабочего процесса")
    
    # Создать нового пользователя
    test_user_id = 333333333
    db.create_user(test_user_id, "workflow_test", "Elementary")
    print(f"✅ Создан тестовый пользователь {test_user_id}")
    
    # Шаг 1: Пользователь отвечает на открытый вопрос
    print("\n📝 Шаг 1: Пользователь отвечает на открытый вопрос...")
    db.save_open_answer(
        test_user_id,
        "EL-WORKFLOW-D5-RV1",
        "What is your favorite hobby and why?",
        "My favorite hobby is reading books. I love it because it helps me learn new things and relax."
    )
    print("✅ Ответ сохранен")
    
    # Также сохраняем в user_progress как непроверенный
    db.save_task_answer(
        test_user_id,
        "EL-WORKFLOW-D5-RV1",
        "review",
        "My favorite hobby is reading books...",
        None  # Не проверено
    )
    print("✅ Ответ сохранен в прогресс")
    
    # Шаг 2: Получить непроверенные ответы для преподавателя
    print("\n📋 Шаг 2: Преподаватель получает непроверенные ответы...")
    unchecked = db.get_unchecked_answers()
    print(f"   Найдено {len(unchecked)} непроверенных ответов")
    
    # Найти наш ответ
    our_answer = None
    for answer in unchecked:
        if answer['user_id'] == test_user_id:
            our_answer = answer
            break
    
    if our_answer:
        print(f"\n   📝 Ответ пользователя {test_user_id}:")
        print(f"      Question: {our_answer['question']}")
        print(f"      Answer: {our_answer['user_answer']}")
    
    # Шаг 3: Преподаватель проверяет ответ
    print("\n✅ Шаг 3: Преподаватель проверяет ответ...")
    if our_answer:
        db.mark_answer_as_checked(our_answer['id'])
        print(f"   Ответ {our_answer['id']} помечен как проверенный")
    
    # Шаг 4: Проверка статуса
    print("\n📊 Шаг 4: Проверка финального статуса...")
    user_answers = db.get_user_open_answers(test_user_id)
    if user_answers:
        answer = user_answers[0]
        status = "Проверен" if answer['checked'] else "Ожидает проверки"
        print(f"   Статус ответа: {status}")
        print(f"   ✅ Рабочий процесс завершен успешно!")


def test_statistics(db: DatabaseManager):
    """Тест статистики по открытым вопросам"""
    print_section("Тест 7: Статистика по открытым вопросам")
    
    # Получить все ответы
    all_unchecked = db.get_unchecked_answers()
    
    # Подсчитать статистику
    users_with_answers = {}
    for answer in all_unchecked:
        user_id = answer['user_id']
        if user_id not in users_with_answers:
            users_with_answers[user_id] = {
                'username': answer['username'],
                'level': answer['level'],
                'count': 0
            }
        users_with_answers[user_id]['count'] += 1
    
    print("\n📊 Статистика непроверенных ответов:")
    print(f"   Всего непроверенных ответов: {len(all_unchecked)}")
    print(f"   Пользователей с непроверенными ответами: {len(users_with_answers)}")
    
    if users_with_answers:
        print("\n   По пользователям:")
        for user_id, info in users_with_answers.items():
            print(f"      User {user_id} ({info['username']}, {info['level']}): {info['count']} ответов")


def main():
    """Главная функция тестирования"""
    print("=" * 70)
    print("  🧪 ТЕСТИРОВАНИЕ ОПЕРАЦИЙ С ОТКРЫТЫМИ ВОПРОСАМИ")
    print("=" * 70)
    print()
    
    # Создать тестовую базу данных
    test_db_path = "test_open_answers.db"
    
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
        test_save_open_answer(db)
        answers = test_get_unchecked_answers(db)
        test_mark_answer_as_checked(db, answers)
        test_get_unchecked_after_marking(db)
        test_get_user_open_answers(db)
        test_workflow_simulation(db)
        test_statistics(db)
        
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

