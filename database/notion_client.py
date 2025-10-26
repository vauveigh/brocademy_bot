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
from dataclasses import dataclass
from notion_client import Client
from notion_client.errors import APIResponseError, RequestTimeoutError

from config.config import config


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Task:
    """
    Класс для представления задания из Notion.
    
    Attributes:
        task_id (str): ID задания (например, "BEG-FAMILY-D1-G1")
        theme (str): Название темы (например, "Family and Friends")
        theme_order (int): Порядковый номер темы (1, 2, 3...)
        level (str): Уровень сложности (Beginner/Elementary/Advanced)
        task_type (str): Тип задания (grammar/reading/vocabulary/situations/review)
        day (int): День цикла (1-5)
        task_number (int): Номер задания в дне (1-3)
        question (str): Текст вопроса
        answer_type (str): Тип ответа (multiple_choice/open_question)
        answer_options (List[str]): Варианты ответов (для multiple_choice)
        correct_answer (str): Правильный ответ
        explanation (Optional[str]): Объяснение (может быть None)
        media_url (Optional[str]): URL медиафайла (может быть None)
        media_type (str): Тип медиа (none/image/audio/video)
        status (str): Статус задания (active/draft/archived)
        notion_page_id (str): ID страницы в Notion (для обратной связи)
        
    Example:
        >>> task = Task(
        ...     task_id="BEG-FAMILY-D1-G1",
        ...     theme="Family and Friends",
        ...     level="Beginner",
        ...     question="Choose the correct answer",
        ...     answer_options=["my", "mine", "me", "I"],
        ...     correct_answer="my"
        ... )
    """
    task_id: str
    theme: str
    theme_order: int
    level: str
    task_type: str
    day: int
    task_number: int
    question: str
    answer_type: str
    answer_options: List[str]
    correct_answer: str
    explanation: Optional[str]
    media_url: Optional[str]
    media_type: str
    status: str
    notion_page_id: str
    
    def has_media(self) -> bool:
        """Проверить, есть ли медиафайл у задания."""
        return self.media_type != "none" and self.media_url is not None
    
    def is_multiple_choice(self) -> bool:
        """Проверить, является ли задание с выбором ответа."""
        return self.answer_type == "multiple_choice"
    
    def is_open_question(self) -> bool:
        """Проверить, является ли задание открытым вопросом."""
        return self.answer_type == "open_question"
    
    def has_explanation(self) -> bool:
        """Проверить, есть ли объяснение у задания."""
        return self.explanation is not None and self.explanation.strip() != ""
    
    def __str__(self) -> str:
        """Строковое представление задания."""
        return f"Task({self.task_id}, {self.theme}, Day {self.day}, #{self.task_number})"


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
            query_params = {}
            
            if filter_conditions:
                if len(filter_conditions) == 1:
                    query_params["filter"] = filter_conditions[0]
                else:
                    query_params["filter"] = {
                        "and": filter_conditions
                    }
            
            # Выполняем запрос
            response = self.client.databases.query(
                database_id=self.database_id,
                **query_params
            )
            count = len(response.get("results", []))
            
            # Обрабатываем пагинацию (если больше 100 результатов)
            while response.get("has_more"):
                response = self.client.databases.query(
                    database_id=self.database_id,
                    start_cursor=response.get("next_cursor"),
                    **query_params
                )
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
    
    def get_task(
        self,
        level: str,
        theme_order: int,
        day: int,
        task_number: int
    ) -> Optional[Task]:
        """
        Получить конкретное задание из Notion.
        
        Args:
            level: Уровень сложности (Beginner/Elementary/Advanced)
            theme_order: Порядковый номер темы
            day: День цикла (1-5)
            task_number: Номер задания в дне (1-3)
            
        Returns:
            Объект Task или None если задание не найдено.
            
        Raises:
            NotionDataError: Если произошла ошибка при получении задания.
            
        Example:
            >>> notion = NotionClient()
            >>> task = notion.get_task("Beginner", 1, 1, 1)
            >>> if task:
            ...     print(f"Task: {task.question}")
            ...     print(f"Options: {task.answer_options}")
        """
        try:
            # Формируем фильтр для поиска задания
            # Все числовые поля используют number filter
            filter_query = {
                "and": [
                    {"property": "Уровень", "select": {"equals": level}},
                    {"property": "Порядок темы", "number": {"equals": theme_order}},
                    {"property": "День цикла", "number": {"equals": day}},
                    {"property": "Номер в дне", "number": {"equals": task_number}},
                    {"property": "Статус", "select": {"equals": "active"}}
                ]
            }
            
            # Выполняем запрос
            response = self.client.databases.query(
                database_id=self.database_id,
                filter=filter_query
            )
            
            results = response.get("results", [])
            
            if not results:
                logger.warning(
                    f"⚠️ Task not found: {level}, theme #{theme_order}, "
                    f"day {day}, task {task_number}"
                )
                return None
            
            if len(results) > 1:
                logger.warning(
                    f"⚠️ Multiple tasks found ({len(results)}), using first one"
                )
            
            # Парсим первое найденное задание
            page = results[0]
            task = self._parse_task(page)
            
            logger.info(f"✅ Task retrieved: {task.task_id}")
            return task
            
        except APIResponseError as e:
            error_msg = f"Failed to get task: {e.code} - {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise NotionDataError(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error getting task: {e}"
            logger.error(f"❌ {error_msg}")
            raise NotionDataError(error_msg)
    
    def get_theme_info(self, level: str, theme_order: int) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о теме.
        
        Args:
            level: Уровень сложности
            theme_order: Порядковый номер темы
            
        Returns:
            Словарь с информацией о теме:
            {
                "theme_name": "Family and Friends",
                "theme_order": 1,
                "level": "Beginner",
                "total_tasks": 15
            }
            Или None если тема не найдена.
            
        Example:
            >>> notion = NotionClient()
            >>> theme_info = notion.get_theme_info("Beginner", 1)
            >>> if theme_info:
            ...     print(f"Theme: {theme_info['theme_name']}")
        """
        try:
            # Получаем любое задание этой темы для извлечения названия
            filter_query = {
                "and": [
                    {"property": "Уровень", "select": {"equals": level}},
                    {"property": "Порядок темы", "number": {"equals": theme_order}},
                    {"property": "Статус", "select": {"equals": "active"}}
                ]
            }
            
            response = self.client.databases.query(
                database_id=self.database_id,
                filter=filter_query,
                page_size=1  # Нам нужна только одна запись
            )
            
            results = response.get("results", [])
            
            if not results:
                logger.warning(
                    f"⚠️ Theme not found: {level}, theme order {theme_order}"
                )
                return None
            
            # Извлекаем название темы из первой записи
            page = results[0]
            properties = page.get("properties", {})
            
            theme_name = self._extract_select(properties.get("Тема", {}))
            
            # Подсчитываем общее количество заданий темы
            total_response = self.client.databases.query(
                database_id=self.database_id,
                filter=filter_query
            )
            total_tasks = len(total_response.get("results", []))
            
            theme_info = {
                "theme_name": theme_name,
                "theme_order": theme_order,
                "level": level,
                "total_tasks": total_tasks
            }
            
            logger.info(
                f"📖 Theme info: '{theme_name}' (order {theme_order}, "
                f"{total_tasks} tasks)"
            )
            return theme_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get theme info: {e}")
            return None
    
    def get_next_theme_order(self, level: str, current_theme_order: int) -> Optional[int]:
        """
        Получить номер следующей темы.
        
        Args:
            level: Уровень сложности
            current_theme_order: Текущий порядковый номер темы
            
        Returns:
            Номер следующей темы или None если тем больше нет.
            
        Example:
            >>> notion = NotionClient()
            >>> next_theme = notion.get_next_theme_order("Beginner", 1)
            >>> if next_theme:
            ...     print(f"Next theme order: {next_theme}")
            ... else:
            ...     print("No more themes available")
        """
        try:
            # Ищем темы с порядком больше текущего
            filter_query = {
                "and": [
                    {"property": "Уровень", "select": {"equals": level}},
                    {"property": "Порядок темы", "number": {"greater_than": current_theme_order}},
                    {"property": "Статус", "select": {"equals": "active"}}
                ]
            }
            
            # Сортируем по возрастанию и берем первую
            response = self.client.databases.query(
                database_id=self.database_id,
                filter=filter_query,
                sorts=[{"property": "Порядок темы", "direction": "ascending"}],
                page_size=1
            )
            
            results = response.get("results", [])
            
            if not results:
                logger.info(
                    f"ℹ️ No more themes after order {current_theme_order} "
                    f"for level {level}"
                )
                return None
            
            # Извлекаем номер следующей темы
            page = results[0]
            properties = page.get("properties", {})
            next_order = self._extract_number(properties.get("Порядок темы", {}))
            
            logger.info(
                f"➡️ Next theme order: {next_order} "
                f"(after {current_theme_order}, level {level})"
            )
            return next_order
            
        except Exception as e:
            logger.error(f"❌ Failed to get next theme order: {e}")
            return None
    
    def get_available_themes_count(self, level: str) -> int:
        """
        Получить количество доступных тем для уровня.
        
        Args:
            level: Уровень сложности
            
        Returns:
            Количество уникальных тем для данного уровня.
            
        Example:
            >>> notion = NotionClient()
            >>> count = notion.get_available_themes_count("Beginner")
            >>> print(f"Available themes: {count}")
        """
        try:
            # Получаем все активные задания этого уровня
            filter_query = {
                "and": [
                    {"property": "Уровень", "select": {"equals": level}},
                    {"property": "Статус", "select": {"equals": "active"}}
                ]
            }
            
            response = self.client.databases.query(
                database_id=self.database_id,
                filter=filter_query
            )
            
            # Собираем уникальные theme_order
            theme_orders = set()
            for page in response.get("results", []):
                properties = page.get("properties", {})
                theme_order = self._extract_number(properties.get("Порядок темы", {}))
                if theme_order > 0:
                    theme_orders.add(theme_order)
            
            # Обрабатываем пагинацию
            while response.get("has_more"):
                response = self.client.databases.query(
                    database_id=self.database_id,
                    filter=filter_query,
                    start_cursor=response.get("next_cursor")
                )
                
                for page in response.get("results", []):
                    properties = page.get("properties", {})
                    theme_order = self._extract_number(properties.get("Порядок темы", {}))
                    if theme_order > 0:
                        theme_orders.add(theme_order)
            
            count = len(theme_orders)
            logger.info(f"📚 Available themes for {level}: {count}")
            return count
            
        except Exception as e:
            logger.error(f"❌ Failed to count available themes: {e}")
            return 0
    
    def get_all_themes_for_level(self, level: str) -> List[Dict[str, Any]]:
        """
        Получить список всех тем для уровня с их информацией.
        
        Args:
            level: Уровень сложности
            
        Returns:
            Список словарей с информацией о каждой теме:
            [
                {
                    "theme_name": "Family and Friends",
                    "theme_order": 1,
                    "level": "Beginner",
                    "total_tasks": 15
                },
                ...
            ]
            
        Example:
            >>> notion = NotionClient()
            >>> themes = notion.get_all_themes_for_level("Beginner")
            >>> for theme in themes:
            ...     print(f"{theme['theme_order']}. {theme['theme_name']} ({theme['total_tasks']} tasks)")
        """
        try:
            # Получаем все активные задания этого уровня
            filter_query = {
                "and": [
                    {"property": "Уровень", "select": {"equals": level}},
                    {"property": "Статус", "select": {"equals": "active"}}
                ]
            }
            
            response = self.client.databases.query(
                database_id=self.database_id,
                filter=filter_query,
                sorts=[{"property": "Порядок темы", "direction": "ascending"}]
            )
            
            # Собираем информацию о темах
            themes_dict = {}
            for page in response.get("results", []):
                properties = page.get("properties", {})
                theme_order = self._extract_number(properties.get("Порядок темы", {}))
                theme_name = self._extract_select(properties.get("Тема", {}))
                
                if theme_order > 0:
                    if theme_order not in themes_dict:
                        themes_dict[theme_order] = {
                            "theme_name": theme_name,
                            "theme_order": theme_order,
                            "level": level,
                            "total_tasks": 0
                        }
                    themes_dict[theme_order]["total_tasks"] += 1
            
            # Обрабатываем пагинацию
            while response.get("has_more"):
                response = self.client.databases.query(
                    database_id=self.database_id,
                    filter=filter_query,
                    start_cursor=response.get("next_cursor"),
                    sorts=[{"property": "Порядок темы", "direction": "ascending"}]
                )
                
                for page in response.get("results", []):
                    properties = page.get("properties", {})
                    theme_order = self._extract_number(properties.get("Порядок темы", {}))
                    theme_name = self._extract_select(properties.get("Тема", {}))
                    
                    if theme_order > 0:
                        if theme_order not in themes_dict:
                            themes_dict[theme_order] = {
                                "theme_name": theme_name,
                                "theme_order": theme_order,
                                "level": level,
                                "total_tasks": 0
                            }
                        themes_dict[theme_order]["total_tasks"] += 1
            
            # Сортируем по theme_order
            themes_list = sorted(themes_dict.values(), key=lambda x: x["theme_order"])
            
            logger.info(f"📚 Retrieved {len(themes_list)} themes for {level}")
            return themes_list
            
        except Exception as e:
            logger.error(f"❌ Failed to get all themes: {e}")
            return []
    
    def _parse_task(self, page: Dict[str, Any]) -> Task:
        """
        Парсинг страницы Notion в объект Task.
        
        Args:
            page: Объект страницы из Notion API
            
        Returns:
            Объект Task с заполненными полями
        """
        properties = page.get("properties", {})
        page_id = page.get("id", "")
        
        # Извлекаем все поля
        task_id = self._extract_title(properties.get("ID задания", {}).get("title", []))
        theme = self._extract_select(properties.get("Тема", {}))
        theme_order = self._extract_number(properties.get("Порядок темы", {}))
        level = self._extract_select(properties.get("Уровень", {}))
        task_type = self._extract_select(properties.get("Тип задания", {}))
        day = self._extract_number(properties.get("День цикла", {}))
        task_number = self._extract_number(properties.get("Номер в дне", {}))
        question = self._extract_rich_text(properties.get("Вопрос", {}))
        answer_type = self._extract_select(properties.get("Тип ответа", {}))
        answer_options_raw = self._extract_rich_text(properties.get("Варианты ответов", {}))
        correct_answer = self._extract_rich_text(properties.get("Правильный ответ", {}))
        explanation = self._extract_rich_text(properties.get("Объяснение", {}))
        media_url = self._extract_url(properties.get("URL медиа", {}))
        media_type = self._extract_select(properties.get("Тип медиа", {}))
        status = self._extract_select(properties.get("Статус", {}))
        
        # Обработка вариантов ответа (split по "|")
        answer_options = []
        if answer_options_raw:
            answer_options = [
                option.strip()
                for option in answer_options_raw.split("|")
                if option.strip()
            ]
        
        # Создаем объект Task
        task = Task(
            task_id=task_id,
            theme=theme,
            theme_order=theme_order,
            level=level,
            task_type=task_type,
            day=day,
            task_number=task_number,
            question=question,
            answer_type=answer_type,
            answer_options=answer_options,
            correct_answer=correct_answer,
            explanation=explanation if explanation else None,
            media_url=media_url if media_url else None,
            media_type=media_type,
            status=status,
            notion_page_id=page_id
        )
        
        return task
    
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
    
    @staticmethod
    def _extract_rich_text(property_data: Dict[str, Any]) -> str:
        """
        Извлечь текст из rich_text поля Notion.
        
        Args:
            property_data: Данные rich_text свойства
            
        Returns:
            Извлеченный текст или пустая строка
        """
        rich_text_array = property_data.get("rich_text", [])
        if not rich_text_array:
            return ""
        
        return "".join(
            item.get("plain_text", "")
            for item in rich_text_array
        )
    
    @staticmethod
    def _extract_select(property_data: Dict[str, Any]) -> str:
        """
        Извлечь значение из select поля Notion.
        
        Args:
            property_data: Данные select свойства
            
        Returns:
            Выбранное значение или пустая строка
        """
        select_data = property_data.get("select")
        if select_data and isinstance(select_data, dict):
            return select_data.get("name", "")
        return ""
    
    @staticmethod
    def _extract_number(property_data: Dict[str, Any]) -> int:
        """
        Извлечь число из number поля Notion.
        
        Args:
            property_data: Данные number свойства
            
        Returns:
            Число или 0
        """
        number = property_data.get("number")
        if number is not None:
            return int(number)
        return 0
    
    @staticmethod
    def _extract_url(property_data: Dict[str, Any]) -> Optional[str]:
        """
        Извлечь URL из url поля Notion.
        
        Args:
            property_data: Данные url свойства
            
        Returns:
            URL или None
        """
        url = property_data.get("url")
        return url if url else None


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
        
        # Тестирование получения задания
        print("8️⃣ Testing task retrieval...")
        if total_tasks > 0 and levels:
            # Пробуем получить первое задание первой темы первого уровня
            test_level = levels[0]
            test_task = notion.get_task(test_level, 1, 1, 1)
            
            if test_task:
                print(f"   ✅ Task retrieved successfully!")
                print(f"   📝 ID: {test_task.task_id}")
                print(f"   📚 Theme: {test_task.theme}")
                print(f"   ❓ Question: {test_task.question[:60]}...")
                print(f"   🎯 Type: {test_task.answer_type}")
                if test_task.is_multiple_choice():
                    print(f"   📋 Options: {len(test_task.answer_options)} variants")
                    print(f"      {' | '.join(test_task.answer_options[:3])}")
                print(f"   ✅ Correct answer: {test_task.correct_answer}")
                if test_task.has_explanation():
                    print(f"   💡 Has explanation: Yes")
                if test_task.has_media():
                    print(f"   🎨 Media: {test_task.media_type}")
            else:
                print("   ⚠️  No task found (theme 1, day 1, task 1)")
                print("   💡 Add tasks to Notion to test task retrieval")
        else:
            print("   ⏭️  Skipped (no tasks in database)")
        print()
        
        # Тестирование получения информации о теме
        print("9️⃣ Testing theme info retrieval...")
        if total_tasks > 0 and levels:
            test_level = levels[0]
            theme_info = notion.get_theme_info(test_level, 1)
            
            if theme_info:
                print(f"   ✅ Theme info retrieved successfully!")
                print(f"   📖 Theme name: {theme_info['theme_name']}")
                print(f"   🔢 Theme order: {theme_info['theme_order']}")
                print(f"   📚 Level: {theme_info['level']}")
                print(f"   📊 Total tasks: {theme_info['total_tasks']}")
            else:
                print("   ⚠️  Theme info not found")
        else:
            print("   ⏭️  Skipped (no tasks in database)")
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

