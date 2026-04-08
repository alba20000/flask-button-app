import sqlite3

DB_NAME = "data/app.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS counter (
            id INTEGER PRIMARY KEY,
            value INTEGER NOT NULL
        )
    """)

    # создаем запись если её нет
    cursor.execute("SELECT COUNT(*) FROM counter")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO counter (value) VALUES (0)")

    conn.commit()
    conn.close()


def get_counter():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM counter WHERE id = 1")
    value = cursor.fetchone()[0]

    conn.close()
    return value


def increment_counter():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("UPDATE counter SET value = value + 1 WHERE id = 1")
    conn.commit()

    cursor.execute("SELECT value FROM counter WHERE id = 1")
    value = cursor.fetchone()[0]

    conn.close()
    return value