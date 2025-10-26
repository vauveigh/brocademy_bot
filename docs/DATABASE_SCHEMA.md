# Схема базы данных SQLite

## Обзор

SQLite база данных используется для хранения данных о пользователях, их прогрессе и ответах на открытые вопросы. База данных состоит из трех основных таблиц.

## Таблицы

### 1. Таблица `users`

Хранит информацию о пользователях и их текущем прогрессе в обучении.

#### SQL схема

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    level TEXT NOT NULL,
    current_day INTEGER DEFAULT 1,
    current_theme TEXT,
    theme_order INTEGER DEFAULT 1,
    task_in_day INTEGER DEFAULT 1,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_task_date DATE
);
```

#### Описание полей

| Поле | Тип | Описание |
|------|-----|----------|
| `user_id` | INTEGER | **PRIMARY KEY**. Telegram user ID пользователя |
| `username` | TEXT | Telegram username пользователя (может быть NULL) |
| `level` | TEXT | Уровень сложности: `Beginner`, `Elementary`, `Advanced` |
| `current_day` | INTEGER | Текущий день цикла (1-5) |
| `current_theme` | TEXT | Название текущей темы (например, "Family and Friends") |
| `theme_order` | INTEGER | Порядковый номер текущей темы (для фильтрации в Notion) |
| `task_in_day` | INTEGER | Номер текущего задания в дне (1-3) |
| `started_at` | TIMESTAMP | Дата и время регистрации пользователя |
| `last_task_date` | DATE | Дата последнего выполненного задания (для трекинга ежедневной активности) |

#### Индексы

```sql
CREATE INDEX idx_users_level ON users(level);
CREATE INDEX idx_users_theme_order ON users(theme_order);
```

#### Примеры записей

```sql
-- Пользователь только начал, выполнил первое задание
INSERT INTO users VALUES (
    123456789,
    'john_doe',
    'Beginner',
    1,
    'Family and Friends',
    1,
    2,
    '2024-10-25 10:30:00',
    '2024-10-25'
);

-- Пользователь на третьей теме, второй день
INSERT INTO users VALUES (
    987654321,
    'jane_smith',
    'Elementary',
    2,
    'Travel and Tourism',
    3,
    1,
    '2024-10-15 09:00:00',
    '2024-10-25'
);
```

#### Логика обновления

**После выполнения задания:**
```python
# Увеличиваем task_in_day
UPDATE users 
SET task_in_day = task_in_day + 1,
    last_task_date = CURRENT_DATE
WHERE user_id = ?;

# Если выполнены все 3 задания дня (task_in_day > 3)
UPDATE users 
SET current_day = current_day + 1,
    task_in_day = 1,
    last_task_date = CURRENT_DATE
WHERE user_id = ? AND task_in_day > 3;

# Если завершен цикл (current_day > 5)
UPDATE users 
SET theme_order = theme_order + 1,
    current_day = 1,
    task_in_day = 1,
    current_theme = [название новой темы из Notion],
    last_task_date = CURRENT_DATE
WHERE user_id = ? AND current_day > 5;
```

---

### 2. Таблица `user_progress`

Хранит историю выполнения всех заданий (для статистики и аналитики).

#### SQL схема

```sql
CREATE TABLE user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_id TEXT NOT NULL,
    task_type TEXT NOT NULL,
    answer TEXT,
    is_correct BOOLEAN,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### Описание полей

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | INTEGER | **PRIMARY KEY**. Автоинкрементный ID записи |
| `user_id` | INTEGER | **FOREIGN KEY**. ID пользователя из таблицы `users` |
| `task_id` | TEXT | ID задания из Notion (например, "BEG-FAMILY-D1-G1") |
| `task_type` | TEXT | Тип задания: `grammar`, `reading`, `vocabulary`, `situations`, `review` |
| `answer` | TEXT | Ответ пользователя (текст или выбранный вариант) |
| `is_correct` | BOOLEAN | Правильность ответа: 1 (правильно), 0 (неправильно), NULL (не проверено - для open_question) |
| `answered_at` | TIMESTAMP | Дата и время ответа |

#### Индексы

```sql
CREATE INDEX idx_progress_user_id ON user_progress(user_id);
CREATE INDEX idx_progress_task_id ON user_progress(task_id);
CREATE INDEX idx_progress_answered_at ON user_progress(answered_at);
```

#### Примеры записей

```sql
-- Multiple choice задание (автоматически проверено)
INSERT INTO user_progress (user_id, task_id, task_type, answer, is_correct) 
VALUES (123456789, 'BEG-FAMILY-D1-G1', 'grammar', 'my', 1);

-- Open question (не проверено)
INSERT INTO user_progress (user_id, task_id, task_type, answer, is_correct) 
VALUES (123456789, 'BEG-FAMILY-D5-RV3', 'review', 'My family is very friendly.', NULL);
```

#### Запросы для статистики

**Процент правильных ответов пользователя:**
```sql
SELECT 
    ROUND(SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM user_progress
WHERE user_id = ? AND is_correct IS NOT NULL;
```

**Количество выполненных заданий:**
```sql
SELECT COUNT(*) as total_tasks
FROM user_progress
WHERE user_id = ?;
```

**Количество дней подряд:**
```sql
SELECT COUNT(DISTINCT DATE(answered_at)) as streak_days
FROM user_progress
WHERE user_id = ?
  AND DATE(answered_at) >= DATE('now', '-30 days');
```

**Статистика по типам заданий:**
```sql
SELECT 
    task_type,
    COUNT(*) as total,
    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
FROM user_progress
WHERE user_id = ? AND is_correct IS NOT NULL
GROUP BY task_type;
```

---

### 3. Таблица `user_answers`

Хранит ответы на открытые вопросы (open_question) для проверки преподавателем.

#### SQL схема

```sql
CREATE TABLE user_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_id TEXT NOT NULL,
    question TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checked BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### Описание полей

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | INTEGER | **PRIMARY KEY**. Автоинкрементный ID записи |
| `user_id` | INTEGER | **FOREIGN KEY**. ID пользователя из таблицы `users` |
| `task_id` | TEXT | ID задания из Notion |
| `question` | TEXT | Текст вопроса (для удобства преподавателя) |
| `user_answer` | TEXT | Ответ пользователя |
| `created_at` | TIMESTAMP | Дата и время отправки ответа |
| `checked` | BOOLEAN | Статус проверки: 0 (не проверено), 1 (проверено) |

#### Индексы

```sql
CREATE INDEX idx_answers_user_id ON user_answers(user_id);
CREATE INDEX idx_answers_checked ON user_answers(checked);
CREATE INDEX idx_answers_created_at ON user_answers(created_at);
```

#### Примеры записей

```sql
-- Непроверенный ответ
INSERT INTO user_answers (user_id, task_id, question, user_answer, checked) 
VALUES (
    123456789, 
    'BEG-FAMILY-D5-RV3', 
    'Describe your family in 3-4 sentences.',
    'My family is small. I have a mother, father and sister. We live in Moscow. We are very happy.',
    0
);

-- Проверенный ответ
INSERT INTO user_answers (user_id, task_id, question, user_answer, checked, created_at) 
VALUES (
    987654321,
    'EL-WORK-D4-S2',
    'How would you introduce yourself in a job interview?',
    'Hello, my name is Jane. I have 5 years of experience in marketing. I am good at social media.',
    1,
    '2024-10-24 14:30:00'
);
```

#### Запросы для веб-интерфейса преподавателя

**Получить все непроверенные ответы:**
```sql
SELECT 
    ua.id,
    u.username,
    u.level,
    ua.task_id,
    ua.question,
    ua.user_answer,
    ua.created_at
FROM user_answers ua
JOIN users u ON ua.user_id = u.user_id
WHERE ua.checked = 0
ORDER BY ua.created_at ASC;
```

**Отметить ответ как проверенный:**
```sql
UPDATE user_answers
SET checked = 1
WHERE id = ?;
```

**Фильтр по пользователю:**
```sql
SELECT * FROM user_answers
WHERE user_id = ?
ORDER BY created_at DESC;
```

---

## Инициализация базы данных

### Скрипт создания всех таблиц

```python
import sqlite3

def init_database(db_path='bot_database.db'):
    """Инициализация базы данных"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создание таблицы users
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
    
    # Создание индексов
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_level ON users(level)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_theme_order ON users(theme_order)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_progress_user_id ON user_progress(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_progress_task_id ON user_progress(task_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_progress_answered_at ON user_progress(answered_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_answers_user_id ON user_answers(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_answers_checked ON user_answers(checked)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_answers_created_at ON user_answers(created_at)')
    
    conn.commit()
    conn.close()
    print(f"База данных инициализирована: {db_path}")

if __name__ == '__main__':
    init_database()
```

---

## Миграция данных

### Миграция со старой схемы на новую

Если у вас уже есть база данных со старой схемой (без полей `current_theme`, `theme_order`, `task_in_day`), используйте этот скрипт:

```python
import sqlite3

def migrate_database(db_path='bot_database.db'):
    """Миграция базы данных к новой схеме"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Добавление новых полей в users
        cursor.execute('ALTER TABLE users ADD COLUMN current_theme TEXT')
        cursor.execute('ALTER TABLE users ADD COLUMN theme_order INTEGER DEFAULT 1')
        cursor.execute('ALTER TABLE users ADD COLUMN task_in_day INTEGER DEFAULT 1')
        
        # Обновление уровней (если использовались старые названия)
        cursor.execute("UPDATE users SET level = 'Elementary' WHERE level = 'A2'")
        cursor.execute("UPDATE users SET level = 'Advanced' WHERE level = 'B1'")
        
        # Инициализация theme_order для существующих пользователей
        cursor.execute('UPDATE users SET theme_order = 1 WHERE theme_order IS NULL')
        cursor.execute('UPDATE users SET task_in_day = 1 WHERE task_in_day IS NULL')
        
        conn.commit()
        print("Миграция выполнена успешно")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Миграция уже была выполнена ранее")
        else:
            raise e
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
```

---

## Резервное копирование

### Скрипт бэкапа

```python
import sqlite3
import shutil
from datetime import datetime

def backup_database(db_path='bot_database.db', backup_dir='backups/'):
    """Создание резервной копии базы данных"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{backup_dir}backup_{timestamp}.db"
    
    shutil.copy2(db_path, backup_path)
    print(f"Резервная копия создана: {backup_path}")
    
    return backup_path
```

### Автоматический бэкап

Рекомендуется настроить автоматический бэкап:
- Ежедневно (cron или Windows Task Scheduler)
- Перед обновлением структуры
- Перед миграцией данных

---

## Оптимизация производительности

### Настройки SQLite

```python
def optimize_database(conn):
    """Оптимизация производительности SQLite"""
    cursor = conn.cursor()
    
    # Включение WAL mode для лучшей concurrency
    cursor.execute('PRAGMA journal_mode=WAL')
    
    # Увеличение cache size
    cursor.execute('PRAGMA cache_size=10000')
    
    # Синхронизация NORMAL (компромисс между скоростью и безопасностью)
    cursor.execute('PRAGMA synchronous=NORMAL')
    
    conn.commit()
```

### VACUUM

Периодически запускайте VACUUM для оптимизации:

```python
def vacuum_database(db_path='bot_database.db'):
    """Очистка и оптимизация базы данных"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('VACUUM')
    conn.close()
    print("VACUUM выполнен успешно")
```

---

## Безопасность

### Лучшие практики

1. **Используйте параметризованные запросы** (защита от SQL injection):
```python
# ✅ Правильно
cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))

# ❌ Неправильно
cursor.execute(f'SELECT * FROM users WHERE user_id = {user_id}')
```

2. **Ограничьте права доступа** к файлу базы данных:
```bash
chmod 600 bot_database.db
```

3. **Регулярно делайте бэкапы**

4. **Валидируйте входные данные** перед записью в БД

---

## Мониторинг

### Полезные запросы для мониторинга

**Количество активных пользователей:**
```sql
SELECT COUNT(*) FROM users;
```

**Пользователи по уровням:**
```sql
SELECT level, COUNT(*) as count
FROM users
GROUP BY level;
```

**Активность за последние 7 дней:**
```sql
SELECT DATE(answered_at) as date, COUNT(*) as tasks_completed
FROM user_progress
WHERE answered_at >= DATE('now', '-7 days')
GROUP BY DATE(answered_at)
ORDER BY date;
```

**Непроверенные ответы:**
```sql
SELECT COUNT(*) as unchecked_answers
FROM user_answers
WHERE checked = 0;
```

---

## Заключение

Эта схема базы данных обеспечивает:
- ✅ Отслеживание прогресса каждого пользователя
- ✅ Хранение истории всех ответов
- ✅ Управление открытыми вопросами для преподавателя
- ✅ Статистику и аналитику
- ✅ Масштабируемость для тысяч пользователей
- ✅ Простоту миграции и обслуживания

