"""
Тестовый скрипт для проверки подключения к Notion.

Этот скрипт проверяет:
1. Наличие credentials в .env файле
2. Подключение к Notion API
3. Доступ к базе данных
4. Базовую информацию о БД

Запуск: python -m database.test_notion_connection
"""

import sys
from database.notion_client import NotionClient, NotionConnectionError


def print_section(title: str):
    """Печать красивого заголовка секции"""
    print()
    print("=" * 60)
    print(f" {title}")
    print("=" * 60)
    print()


def test_notion_connection():
    """Основная функция тестирования подключения"""
    
    print_section("🔍 NOTION API CONNECTION TEST")
    
    # Шаг 1: Инициализация
    print("1️⃣ Initializing Notion client...")
    try:
        notion = NotionClient()
        print("   ✅ Client initialized successfully")
    except NotionConnectionError as e:
        print(f"   ❌ Failed to initialize: {e}")
        print("\n💡 Please check:")
        print("   1. .env file exists")
        print("   2. NOTION_API_KEY is set")
        print("   3. NOTION_DATABASE_ID is set")
        return False
    
    # Шаг 2: Тест подключения
    print("\n2️⃣ Testing connection to Notion API...")
    if not notion.test_connection():
        print("   ❌ Connection test failed")
        print("\n💡 Possible issues:")
        print("   1. NOTION_API_KEY is incorrect")
        print("   2. NOTION_DATABASE_ID is incorrect")
        print("   3. Integration doesn't have access to the database")
        print("\n📖 How to fix:")
        print("   1. Open your database in Notion")
        print("   2. Click '...' → 'Add connections'")
        print("   3. Select your integration")
        print("   4. Re-run this script")
        return False
    
    print("   ✅ Connection successful!")
    
    # Шаг 3: Получение информации о БД
    print("\n3️⃣ Retrieving database information...")
    try:
        db_info = notion.get_database_info()
        print(f"   📊 Database: {db_info['title']}")
        print(f"   🆔 ID: {db_info['id'][:20]}...")
        print(f"   📋 Properties: {len(db_info['properties'])}")
    except Exception as e:
        print(f"   ⚠️  Could not retrieve full info: {e}")
        print("   But connection is working!")
    
    # Шаг 4: Подсчет заданий
    print("\n4️⃣ Counting tasks...")
    try:
        total_tasks = notion.count_tasks()
        print(f"   📊 Total tasks: {total_tasks}")
        
        if total_tasks == 0:
            print("\n   ⚠️  No tasks found in database")
            print("   💡 Add at least one theme (15 tasks) to start using the bot")
    except Exception as e:
        print(f"   ⚠️  Could not count tasks: {e}")
    
    # Успех!
    print_section("✅ CONNECTION TEST PASSED!")
    print("🚀 Notion client is ready to use!")
    print()
    return True


if __name__ == "__main__":
    success = test_notion_connection()
    sys.exit(0 if success else 1)

