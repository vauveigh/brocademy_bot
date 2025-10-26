"""
Тестовый скрипт для запуска бота.

Проверяет конфигурацию и запускает бота.

Использование:
    python test_bot_run.py
"""

import sys
import os

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🤖 TELEGRAM BOT TEST RUNNER")
print("=" * 60)
print()

# Проверка конфигурации
print("1️⃣ Checking configuration...")
try:
    from config.config import config
    
    print("   ✅ Config loaded")
    print(f"   📂 Database path: {config.SQLITE_DB_PATH}")
    
    # Валидация обязательных переменных
    config.validate()
    print("   ✅ Required variables are set")
    
except Exception as e:
    print(f"   ❌ Configuration error: {e}")
    print()
    print("💡 Make sure your .env file has:")
    print("   - TELEGRAM_BOT_TOKEN")
    print("   - NOTION_API_KEY")
    print("   - NOTION_DATABASE_ID")
    sys.exit(1)

print()

# Проверка базы данных
print("2️⃣ Checking database...")
try:
    from database.db_manager import DatabaseManager
    
    db = DatabaseManager(config.SQLITE_DB_PATH)
    db_info = db.check_tables()
    
    if not db_info['db_exists']:
        print("   ⚠️  Database not found, initializing...")
        db.init_database()
        print("   ✅ Database initialized")
    else:
        print(f"   ✅ Database exists ({len(db_info['tables'])} tables)")
    
except Exception as e:
    print(f"   ❌ Database error: {e}")
    sys.exit(1)

print()

# Проверка подключения к Notion
print("3️⃣ Checking Notion connection...")
try:
    from database.notion_client import get_notion_client
    
    notion = get_notion_client()
    if notion.test_connection():
        db_info = notion.get_database_info()
        print(f"   ✅ Connected to Notion: '{db_info['title']}'")
        
        # Проверяем наличие заданий
        total_tasks = notion.count_tasks()
        print(f"   📊 Total tasks in database: {total_tasks}")
        
        if total_tasks == 0:
            print("   ⚠️  WARNING: No tasks found in Notion database!")
            print("   💡 Add tasks to Notion before testing the bot")
    else:
        print("   ❌ Failed to connect to Notion")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Notion connection error: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL CHECKS PASSED!")
print("=" * 60)
print()
print("🚀 Starting bot...")
print("Press Ctrl+C to stop")
print()

# Запуск бота
try:
    from bot.main import main
    import asyncio
    
    asyncio.run(main())
    
except KeyboardInterrupt:
    print()
    print("⌨️  Bot stopped by user")
    print("👋 Goodbye!")
except Exception as e:
    print()
    print(f"❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

