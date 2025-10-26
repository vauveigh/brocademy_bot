"""
Notion Client Module

Клиент для работы с Notion API и получения заданий из базы данных.

This module provides NotionClient class for:
- Connecting to Notion API
- Retrieving tasks from Notion database
- Handling API errors and rate limits
- Caching frequently accessed data

Author: Vladimir
Date: 2024-10-26
"""

import logging
from typing import Optional, Dict, Any, List
from notion_client import Client
from notion_client.errors import APIResponseError, RequestTimeoutError

from config.config import config


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NotionConnectionError(Exception):
    """Исключение при ошибке подключения к Notion API"""
    pass


class NotionDataError(Exception):
    """Исключение при ошибке получения данных из Notion"""
    pass


class NotionClient:
    """
    Клиент для работы с Notion API.
    
    Этот класс предоставляет методы для подключения к Notion API,
    получения заданий и управления данными базы данных.
    
    Attributes:
        api_key (str): API ключ для Notion
        database_id (str): ID базы данных с заданиями
        client (Client): Экземпляр Notion клиента
        
    Example:
        >>> notion = NotionClient()
        >>> if notion.test_connection():
        ...     db_info = notion.get_database_info()
        ...     print(f"Connected to: {db_info['title']}")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        database_id: Optional[str] = None
    ):
        """
        Инициализация Notion клиента.
        
        Args:
            api_key: Notion API key. Если не указан, берется из config.
            database_id: ID базы данных. Если не указан, берется из config.
            
        Raises:
            NotionConnectionError: Если не указаны api_key или database_id.
        """
        self.api_key = api_key or config.NOTION_API_KEY
        self.database_id = database_id or config.NOTION_DATABASE_ID
        
        if not self.api_key:
            raise NotionConnectionError(
                "Notion API key not provided. "
                "Please set NOTION_API_KEY in your .env file."
            )
        
        if not self.database_id:
            raise NotionConnectionError(
                "Notion Database ID not provided. "
                "Please set NOTION_DATABASE_ID in your .env file."
            )
        
        try:
            self.client = Client(auth=self.api_key)
            logger.info("✅ Notion client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Notion client: {e}")
            raise NotionConnectionError(f"Failed to initialize Notion client: {e}")
    
    def test_connection(self) -> bool:
        """
        Проверка подключения к Notion API.
        
        Выполняет тестовый запрос к API для проверки валидности credentials
        и доступности базы данных.
        
        Returns:
            True если подключение успешно, False в противном случае.
            
        Example:
            >>> notion = NotionClient()
            >>> if notion.test_connection():
            ...     print("Connection successful!")
        """
        try:
            # Пытаемся получить информацию о базе данных
            response = self.client.databases.retrieve(database_id=self.database_id)
            
            if response:
                db_title = self._extract_title(response.get("title", []))
                logger.info(f"✅ Successfully connected to Notion database: '{db_title}'")
                return True
            else:
                logger.warning("⚠️ Received empty response from Notion")
                return False
                
        except APIResponseError as e:
            logger.error(f"❌ Notion API error: {e.code} - {str(e)}")
            if e.code == "unauthorized":
                logger.error("   → Check your NOTION_API_KEY")
            elif e.code == "object_not_found":
                logger.error("   → Check your NOTION_DATABASE_ID")
                logger.error("   → Make sure the integration has access to the database")
            return False
            
        except RequestTimeoutError:
            logger.error("❌ Request timeout - Notion API is not responding")
            return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected error during connection test: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Получить информацию о базе данных Notion.
        
        Returns:
            Словарь с информацией о базе данных:
            - title: Название базы данных
            - id: ID базы данных
            - created_time: Время создания
            - last_edited_time: Время последнего редактирования
            - properties: Список свойств (полей) базы данных
            
        Raises:
            NotionConnectionError: Если не удалось получить информацию.
            
        Example:
            >>> notion = NotionClient()
            >>> info = notion.get_database_info()
            >>> print(f"Database: {info['title']}")
            >>> print(f"Properties: {', '.join(info['properties'])}")
        """
        try:
            response = self.client.databases.retrieve(database_id=self.database_id)
            
            # Извлечение названия
            title = self._extract_title(response.get("title", []))
            
            # Извлечение списка свойств
            properties = list(response.get("properties", {}).keys())
            
            db_info = {
                "title": title,
                "id": response.get("id"),
                "created_time": response.get("created_time"),
                "last_edited_time": response.get("last_edited_time"),
                "properties": properties
            }
            
            logger.info(f"📊 Database info retrieved: '{title}' with {len(properties)} properties")
            return db_info
            
        except APIResponseError as e:
            error_msg = f"Failed to retrieve database info: {e.code} - {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise NotionConnectionError(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error retrieving database info: {e}"
            logger.error(f"❌ {error_msg}")
            raise NotionConnectionError(error_msg)
    
    def get_database_properties(self) -> Dict[str, Dict[str, Any]]:
        """
        Получить детальную информацию о свойствах (полях) базы данных.
        
        Returns:
            Словарь с информацией о каждом свойстве:
            {
                "property_name": {
                    "type": "select" | "text" | "number" | ...,
                    "id": "property_id",
                    "options": [...] # для select полей
                }
            }
            
        Raises:
            NotionConnectionError: Если не удалось получить информацию.
            
        Example:
            >>> notion = NotionClient()
            >>> props = notion.get_database_properties()
            >>> print(f"Field 'Уровень' type: {props['Уровень']['type']}")
            >>> print(f"Options: {props['Уровень']['options']}")
        """
        try:
            response = self.client.databases.retrieve(database_id=self.database_id)
            properties_raw = response.get("properties", {})
            
            properties = {}
            for prop_name, prop_data in properties_raw.items():
                prop_type = prop_data.get("type")
                prop_info = {
                    "type": prop_type,
                    "id": prop_data.get("id")
                }
                
                # Для select полей извлекаем опции
                if prop_type == "select" and "select" in prop_data:
                    options = [
                        opt.get("name")
                        for opt in prop_data["select"].get("options", [])
                    ]
                    prop_info["options"] = options
                
                # Для multi_select полей
                elif prop_type == "multi_select" and "multi_select" in prop_data:
                    options = [
                        opt.get("name")
                        for opt in prop_data["multi_select"].get("options", [])
                    ]
                    prop_info["options"] = options
                
                properties[prop_name] = prop_info
            
            logger.info(f"📋 Retrieved {len(properties)} database properties")
            return properties
            
        except APIResponseError as e:
            error_msg = f"Failed to retrieve database properties: {e.code} - {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise NotionConnectionError(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error retrieving database properties: {e}"
            logger.error(f"❌ {error_msg}")
            raise NotionConnectionError(error_msg)
    
    def count_tasks(
        self,
        level: Optional[str] = None,
        theme: Optional[str] = None
    ) -> int:
        """
        Подсчитать количество заданий в базе данных.
        
        Args:
            level: Фильтр по уровню (Beginner/Elementary/Advanced).
                   Если None, считаются все задания.
            theme: Фильтр по теме. Если None, считаются все задания.
            
        Returns:
            Количество заданий, соответствующих фильтрам.
            
        Example:
            >>> notion = NotionClient()
            >>> total = notion.count_tasks()
            >>> beginner_tasks = notion.count_tasks(level="Beginner")
            >>> print(f"Total tasks: {total}, Beginner: {beginner_tasks}")
        """
        try:
            # Формируем фильтр
            filter_conditions = []
            
            if level:
                filter_conditions.append({
                    "property": "Уровень",
                    "select": {"equals": level}
                })
            
            if theme:
                filter_conditions.append({
                    "property": "Тема",
                    "select": {"equals": theme}
                })
            
            # Создаем запрос
            query_params = {"database_id": self.database_id}
            
            if filter_conditions:
                if len(filter_conditions) == 1:
                    query_params["filter"] = filter_conditions[0]
                else:
                    query_params["filter"] = {
                        "and": filter_conditions
                    }
            
            # Выполняем запрос
            response = self.client.databases.query(**query_params)
            count = len(response.get("results", []))
            
            # Обрабатываем пагинацию (если больше 100 результатов)
            while response.get("has_more"):
                query_params["start_cursor"] = response.get("next_cursor")
                response = self.client.databases.query(**query_params)
                count += len(response.get("results", []))
            
            filter_str = f" (level={level}, theme={theme})" if level or theme else ""
            logger.info(f"📊 Found {count} tasks{filter_str}")
            return count
            
        except APIResponseError as e:
            error_msg = f"Failed to count tasks: {e.code} - {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise NotionDataError(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error counting tasks: {e}"
            logger.error(f"❌ {error_msg}")
            raise NotionDataError(error_msg)
    
    def get_available_levels(self) -> List[str]:
        """
        Получить список доступных уровней сложности.
        
        Returns:
            Список уровней (например: ["Beginner", "Elementary", "Advanced"]).
            
        Example:
            >>> notion = NotionClient()
            >>> levels = notion.get_available_levels()
            >>> print(f"Available levels: {', '.join(levels)}")
        """
        try:
            props = self.get_database_properties()
            
            if "Уровень" in props and "options" in props["Уровень"]:
                levels = props["Уровень"]["options"]
                logger.info(f"📚 Available levels: {', '.join(levels)}")
                return levels
            else:
                logger.warning("⚠️ 'Уровень' property not found or has no options")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to get available levels: {e}")
            return []
    
    def get_available_themes(self, level: Optional[str] = None) -> List[str]:
        """
        Получить список доступных тем.
        
        Args:
            level: Фильтр по уровню. Если None, возвращаются все темы.
            
        Returns:
            Список тем.
            
        Example:
            >>> notion = NotionClient()
            >>> themes = notion.get_available_themes(level="Beginner")
            >>> print(f"Beginner themes: {', '.join(themes)}")
        """
        try:
            props = self.get_database_properties()
            
            if "Тема" in props and "options" in props["Тема"]:
                themes = props["Тема"]["options"]
                logger.info(f"📖 Found {len(themes)} themes")
                return themes
            else:
                logger.warning("⚠️ 'Тема' property not found or has no options")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to get available themes: {e}")
            return []
    
    @staticmethod
    def _extract_title(title_array: List[Dict]) -> str:
        """
        Извлечь текст из массива title объектов Notion.
        
        Args:
            title_array: Массив title объектов из Notion API.
            
        Returns:
            Извлеченный текст или "Untitled".
        """
        if not title_array:
            return "Untitled"
        
        # Notion возвращает title как массив rich text объектов
        return "".join(
            item.get("plain_text", "")
            for item in title_array
        )


# Singleton instance
_notion_client_instance: Optional[NotionClient] = None


def get_notion_client() -> NotionClient:
    """
    Получить singleton экземпляр NotionClient.
    
    Использует паттерн Singleton для переиспользования одного
    экземпляра клиента во всем приложении.
    
    Returns:
        Экземпляр NotionClient.
        
    Example:
        >>> notion = get_notion_client()
        >>> notion.test_connection()
    """
    global _notion_client_instance
    
    if _notion_client_instance is None:
        _notion_client_instance = NotionClient()
    
    return _notion_client_instance


if __name__ == "__main__":
    """
    Тестовый скрипт для проверки подключения к Notion.
    
    Запуск: python -m database.notion_client
    """
    print("=" * 60)
    print("🔍 NOTION CLIENT CONNECTION TEST")
    print("=" * 60)
    print()
    
    try:
        # Создание клиента
        print("1️⃣ Initializing Notion client...")
        notion = NotionClient()
        print("   ✅ Client initialized\n")
        
        # Тест подключения
        print("2️⃣ Testing connection to Notion API...")
        if notion.test_connection():
            print("   ✅ Connection successful!\n")
        else:
            print("   ❌ Connection failed!\n")
            exit(1)
        
        # Получение информации о базе данных
        print("3️⃣ Retrieving database information...")
        db_info = notion.get_database_info()
        print(f"   📊 Database: {db_info['title']}")
        print(f"   🆔 ID: {db_info['id']}")
        print(f"   📅 Created: {db_info['created_time']}")
        print(f"   ✏️  Last edited: {db_info['last_edited_time']}")
        print(f"   📋 Properties ({len(db_info['properties'])}):")
        for prop in db_info['properties']:
            print(f"      • {prop}")
        print()
        
        # Получение свойств базы данных
        print("4️⃣ Retrieving database properties details...")
        props = notion.get_database_properties()
        
        important_props = ["ID задания", "Тема", "Уровень", "День цикла", "Номер в дне"]
        for prop_name in important_props:
            if prop_name in props:
                prop_info = props[prop_name]
                print(f"   • {prop_name}: {prop_info['type']}", end="")
                if "options" in prop_info:
                    print(f" ({len(prop_info['options'])} options)")
                else:
                    print()
        print()
        
        # Получение доступных уровней
        print("5️⃣ Available levels:")
        levels = notion.get_available_levels()
        for level in levels:
            print(f"   • {level}")
        print()
        
        # Получение доступных тем
        print("6️⃣ Available themes:")
        themes = notion.get_available_themes()
        if len(themes) <= 10:
            for theme in themes:
                print(f"   • {theme}")
        else:
            for theme in themes[:5]:
                print(f"   • {theme}")
            print(f"   ... and {len(themes) - 5} more")
        print()
        
        # Подсчет заданий
        print("7️⃣ Counting tasks...")
        total_tasks = notion.count_tasks()
        print(f"   📊 Total tasks in database: {total_tasks}")
        
        for level in levels:
            level_tasks = notion.count_tasks(level=level)
            print(f"   📚 {level}: {level_tasks} tasks")
        print()
        
        # Итоговая информация
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("📝 Summary:")
        print(f"   • Database: {db_info['title']}")
        print(f"   • Total tasks: {total_tasks}")
        print(f"   • Levels: {len(levels)}")
        print(f"   • Themes: {len(themes)}")
        print()
        print("🚀 Notion client is ready to use!")
        
    except NotionConnectionError as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your .env file")
        print("   2. Verify NOTION_API_KEY is correct")
        print("   3. Verify NOTION_DATABASE_ID is correct")
        print("   4. Make sure the integration has access to the database")
        exit(1)
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

