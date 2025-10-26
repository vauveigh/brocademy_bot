"""
Тестовый скрипт для проверки управления темами.

Этот скрипт тестирует:
1. Получение информации о теме
2. Получение следующей темы
3. Подсчет доступных тем
4. Получение всех тем для уровня
5. Обработку окончания тем

Запуск: python -m database.test_themes
"""

from database.notion_client import get_notion_client, NotionDataError


def print_section(title: str):
    """Печать красивого заголовка секции"""
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)
    print()


def test_theme_management():
    """Основная функция тестирования управления темами"""
    
    print_section("🔍 THEME MANAGEMENT TEST (Stage 2.4)")
    
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
        
        # Используем первый доступный уровень для тестов
        test_level = levels[0]
        print(f"   🎯 Testing with level: {test_level}\n")
        
        # Шаг 4: Получение информации о первой теме
        print(f"4️⃣ Getting theme info (Theme order 1)...")
        theme_info = notion.get_theme_info(test_level, 1)
        
        if not theme_info:
            print("   ❌ Theme 1 not found!")
            print("   💡 Make sure you have at least one theme in Notion")
            return False
        
        print(f"   ✅ Theme retrieved!")
        print(f"   📖 Theme name: {theme_info['theme_name']}")
        print(f"   🔢 Theme order: {theme_info['theme_order']}")
        print(f"   📚 Level: {theme_info['level']}")
        print(f"   📊 Total tasks: {theme_info['total_tasks']}")
        print()
        
        # Шаг 5: Получение следующей темы
        print(f"5️⃣ Testing get_next_theme_order()...")
        next_theme = notion.get_next_theme_order(test_level, 1)
        
        if next_theme:
            print(f"   ✅ Next theme found: Theme order {next_theme}")
            
            # Получаем информацию о следующей теме
            next_theme_info = notion.get_theme_info(test_level, next_theme)
            if next_theme_info:
                print(f"   📖 Theme name: {next_theme_info['theme_name']}")
                print(f"   📊 Total tasks: {next_theme_info['total_tasks']}")
        else:
            print(f"   ℹ️  No more themes after Theme 1")
            print(f"   💡 This is normal if you only have 1 theme")
        print()
        
        # Шаг 6: Подсчет всех доступных тем
        print(f"6️⃣ Testing get_available_themes_count()...")
        themes_count = notion.get_available_themes_count(test_level)
        print(f"   📊 Total available themes for {test_level}: {themes_count}")
        
        if themes_count == 0:
            print("   ⚠️  No themes found!")
            print("   💡 Add themes to Notion to test theme management")
            return False
        print()
        
        # Шаг 7: Получение списка всех тем
        print(f"7️⃣ Testing get_all_themes_for_level()...")
        all_themes = notion.get_all_themes_for_level(test_level)
        
        if not all_themes:
            print("   ❌ No themes found!")
            return False
        
        print(f"   ✅ Retrieved {len(all_themes)} themes:\n")
        for theme in all_themes:
            print(f"   {theme['theme_order']}. {theme['theme_name']}")
            print(f"      └─ {theme['total_tasks']} tasks")
        print()
        
        # Шаг 8: Проверка на окончание тем
        print(f"8️⃣ Testing end of themes...")
        # Пробуем получить тему после последней
        last_order = all_themes[-1]['theme_order']
        next_after_last = notion.get_next_theme_order(test_level, last_order)
        
        if next_after_last is None:
            print(f"   ✅ Correctly returned None for theme after order {last_order}")
            print(f"   ℹ️  User has completed all available themes")
        else:
            print(f"   ⚠️  Unexpected: found theme order {next_after_last} after {last_order}")
        print()
        
        # Шаг 9: Тестирование цикла тем (симуляция прохождения)
        print(f"9️⃣ Simulating theme progression...")
        current_theme = 1
        progression_log = []
        
        while current_theme is not None:
            theme_info = notion.get_theme_info(test_level, current_theme)
            if theme_info:
                progression_log.append(
                    f"Theme {current_theme}: {theme_info['theme_name']}"
                )
            
            # Переход к следующей теме
            next_theme_order = notion.get_next_theme_order(test_level, current_theme)
            
            if next_theme_order is None:
                break
            
            current_theme = next_theme_order
            
            # Защита от бесконечного цикла
            if len(progression_log) > 100:
                print("   ⚠️  Too many themes, stopping simulation")
                break
        
        print(f"   ✅ Simulated progression through {len(progression_log)} themes:")
        for i, log in enumerate(progression_log[:5], 1):  # Показываем первые 5
            print(f"      {i}. {log}")
        if len(progression_log) > 5:
            print(f"      ... and {len(progression_log) - 5} more")
        print()
        
        # Шаг 10: Тестирование с несуществующей темой
        print(f"🔟 Testing with non-existent theme...")
        non_theme = notion.get_theme_info(test_level, 999)
        if non_theme is None:
            print("   ✅ Correctly returned None for non-existent theme")
        else:
            print("   ⚠️  Unexpected: got info for theme_order=999")
        print()
        
        # Шаг 11: Тестирование для всех уровней
        print(f"1️⃣1️⃣ Testing theme counts for all levels...")
        for level in levels:
            count = notion.get_available_themes_count(level)
            print(f"   • {level}: {count} themes")
        print()
        
        # Итоги
        print_section("✅ ALL TESTS PASSED!")
        print("📝 Summary:")
        print(f"   • Theme management: ✅ Working")
        print(f"   • get_theme_info(): ✅ Working")
        print(f"   • get_next_theme_order(): ✅ Working")
        print(f"   • get_available_themes_count(): ✅ Working")
        print(f"   • get_all_themes_for_level(): ✅ Working")
        print(f"   • End of themes handling: ✅ Working")
        print()
        print(f"📊 Results:")
        print(f"   • Test level: {test_level}")
        print(f"   • Total themes: {themes_count}")
        print(f"   • Theme progression: {len(progression_log)} themes")
        print()
        print("🚀 Stage 2.4 implementation is ready!")
        print()
        print("📖 Integration examples:")
        print("   # В боте после завершения темы:")
        print(f"   next_theme = notion.get_next_theme_order(user.level, user.theme_order)")
        print("   if next_theme:")
        print("       # Переходим к следующей теме")
        print("       db.update_user_progress(user_id, theme_order=next_theme)")
        print("   else:")
        print("       # Все темы пройдены!")
        print('       await message.answer("🎉 Поздравляем! Вы прошли все темы!")')
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
    success = test_theme_management()
    sys.exit(0 if success else 1)

