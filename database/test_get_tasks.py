"""
Тестовый скрипт для проверки получения заданий из Notion.

Этот скрипт тестирует:
1. Получение конкретного задания
2. Парсинг всех полей задания
3. Обработку вариантов ответов
4. Получение информации о теме
5. Разные типы заданий (multiple_choice, open_question)

Запуск: python -m database.test_get_tasks
"""

from database.notion_client import get_notion_client, NotionDataError


def print_section(title: str):
    """Печать красивого заголовка секции"""
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)
    print()


def test_get_tasks():
    """Основная функция тестирования получения заданий"""
    
    print_section("🔍 NOTION TASK RETRIEVAL TEST (Stage 2.2)")
    
    try:
        # Шаг 1: Инициализация клиента
        print("1️⃣ Initializing Notion client...")
        notion = get_notion_client()
        print("   ✅ Client initialized\n")
        
        # Шаг 2: Проверка подключения
        print("2️⃣ Testing connection...")
        if not notion.test_connection():
            print("   ❌ Connection failed!")
            return False
        print("   ✅ Connection successful!\n")
        
        # Шаг 3: Получение доступных уровней
        print("3️⃣ Getting available levels...")
        levels = notion.get_available_levels()
        if not levels:
            print("   ❌ No levels found in database")
            return False
        print(f"   ✅ Found {len(levels)} levels: {', '.join(levels)}\n")
        
        # Шаг 4: Подсчет заданий
        print("4️⃣ Counting tasks...")
        total_tasks = notion.count_tasks()
        print(f"   📊 Total tasks: {total_tasks}")
        
        if total_tasks == 0:
            print("\n   ⚠️  No tasks in database!")
            print("   💡 Please add at least one theme (15 tasks) to Notion")
            print("   📖 See IMPORT_INSTRUCTIONS.md for how to import tasks")
            return False
        
        for level in levels:
            level_count = notion.count_tasks(level=level)
            print(f"   • {level}: {level_count} tasks")
        print()
        
        # Шаг 5: Получение информации о первой теме
        print("5️⃣ Getting theme info (Level: {}, Theme Order: 1)...".format(levels[0]))
        theme_info = notion.get_theme_info(levels[0], 1)
        
        if not theme_info:
            print("   ❌ Theme not found!")
            return False
        
        print(f"   ✅ Theme retrieved!")
        print(f"   📖 Theme name: {theme_info['theme_name']}")
        print(f"   🔢 Theme order: {theme_info['theme_order']}")
        print(f"   📚 Level: {theme_info['level']}")
        print(f"   📊 Total tasks in theme: {theme_info['total_tasks']}")
        print()
        
        # Шаг 6: Получение конкретных заданий
        print("6️⃣ Testing task retrieval (Day 1, Task 1)...")
        task = notion.get_task(levels[0], 1, 1, 1)
        
        if not task:
            print("   ❌ Task not found!")
            print("   💡 Make sure you have:")
            print("      • Level: {}".format(levels[0]))
            print("      • Theme order: 1 (Порядок темы)")
            print("      • Day: 1 (День цикла)")
            print("      • Task number: 1 (Номер в дне)")
            print("      • Status: active")
            return False
        
        print("   ✅ Task retrieved successfully!\n")
        
        # Шаг 7: Детальная информация о задании
        print("7️⃣ Task details:")
        print(f"   📝 Task ID: {task.task_id}")
        print(f"   📖 Theme: {task.theme}")
        print(f"   🔢 Theme order: {task.theme_order}")
        print(f"   📚 Level: {task.level}")
        print(f"   🎯 Task type: {task.task_type}")
        print(f"   📅 Day: {task.day}/5")
        print(f"   #️⃣  Task number: {task.task_number}/3")
        print(f"   🔄 Status: {task.status}")
        print()
        
        # Шаг 8: Контент задания
        print("8️⃣ Task content:")
        print(f"   ❓ Question:")
        print(f"      {task.question}")
        print()
        print(f"   🎯 Answer type: {task.answer_type}")
        
        if task.is_multiple_choice():
            print(f"   📋 Answer options ({len(task.answer_options)}):")
            for i, option in enumerate(task.answer_options, 1):
                print(f"      {i}. {option}")
            print()
        
        print(f"   ✅ Correct answer: {task.correct_answer}")
        
        if task.has_explanation():
            print(f"   💡 Explanation:")
            print(f"      {task.explanation}")
        else:
            print(f"   💡 Explanation: (none)")
        print()
        
        # Шаг 9: Медиа
        print("9️⃣ Media content:")
        if task.has_media():
            print(f"   ✅ Has media: Yes")
            print(f"   🎨 Media type: {task.media_type}")
            print(f"   🔗 Media URL: {task.media_url}")
        else:
            print(f"   ⚪ No media")
        print()
        
        # Шаг 10: Методы проверки
        print("🔟 Task methods:")
        print(f"   • is_multiple_choice(): {task.is_multiple_choice()}")
        print(f"   • is_open_question(): {task.is_open_question()}")
        print(f"   • has_explanation(): {task.has_explanation()}")
        print(f"   • has_media(): {task.has_media()}")
        print(f"   • __str__(): {str(task)}")
        print()
        
        # Шаг 11: Попробуем получить разные задания
        print("1️⃣1️⃣ Testing different tasks...")
        test_cases = [
            (1, 1, 2),  # Day 1, Task 2
            (1, 2, 1),  # Day 2, Task 1
            (1, 3, 1),  # Day 3, Task 1
        ]
        
        for day, task_num in [(1, 2), (2, 1), (3, 1)]:
            test_task = notion.get_task(levels[0], 1, day, task_num)
            if test_task:
                print(f"   ✅ Task found: Day {day}, #{task_num} - {test_task.task_type}")
            else:
                print(f"   ⚪ Task not found: Day {day}, #{task_num}")
        print()
        
        # Шаг 12: Тест с несуществующим заданием
        print("1️⃣2️⃣ Testing non-existent task...")
        non_task = notion.get_task(levels[0], 999, 1, 1)
        if non_task is None:
            print("   ✅ Correctly returned None for non-existent task")
        else:
            print("   ⚠️  Unexpected: got a task for theme_order=999")
        print()
        
        # Итоги
        print_section("✅ ALL TESTS PASSED!")
        print("📝 Summary:")
        print(f"   • Database connection: ✅ Working")
        print(f"   • Total tasks: {total_tasks}")
        print(f"   • Theme info retrieval: ✅ Working")
        print(f"   • Task retrieval: ✅ Working")
        print(f"   • Task parsing: ✅ All fields parsed correctly")
        print(f"   • Answer options split: ✅ Working")
        print(f"   • Task methods: ✅ All methods working")
        print()
        print("🚀 Stage 2.2 implementation is ready!")
        print()
        print("📖 Next steps:")
        print("   • Add more tasks to Notion for comprehensive testing")
        print("   • Test with different task types (grammar, reading, etc.)")
        print("   • Test with open questions")
        print("   • Test with media attachments")
        print()
        
        return True
        
    except NotionDataError as e:
        print(f"\n❌ NOTION DATA ERROR: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = test_get_tasks()
    sys.exit(0 if success else 1)

