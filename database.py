import sqlite3

DB_NAME = "database.db"

# Инициализация базы данных и создание таблицы
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deadlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                task TEXT NOT NULL,
                due_date TEXT NOT NULL
            )
        """)
        conn.commit()

# Добавление нового дедлайна в базу
def add_deadline(user_id, subject, task, due_date):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO deadlines (user_id, subject, task, due_date) VALUES (?, ?, ?, ?)",
            (user_id, subject, task, due_date)
        )
        conn.commit()

# Получение списка всех дедлайнов конкретного пользователя
def get_user_deadlines(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, subject, task, due_date FROM deadlines WHERE user_id = ? ORDER BY due_date",
            (user_id,)
        )
        return cursor.fetchall()