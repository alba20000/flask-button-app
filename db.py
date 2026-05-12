import os
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

DB_HOST = os.environ.get("POSTGRES_HOST", "db")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DB", "appdb")
DB_USER = os.environ.get("POSTGRES_USER", "appuser")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "apppassword")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS counter (
            id SERIAL PRIMARY KEY,
            value INTEGER NOT NULL DEFAULT 0
        )
    """)

    # создаем запись если её нет
    cursor.execute("SELECT COUNT(*) FROM counter")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO counter (value) VALUES (0)")

    # таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL
        )
    """)

    # создаем пользователя по умолчанию если нет
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ("admin",))
    if cursor.fetchone()[0] == 0:
        password_hash = generate_password_hash("admin123")
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", ("admin", password_hash))

    conn.commit()
    cursor.close()
    conn.close()


def get_counter():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM counter WHERE id = 1")
    value = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return value


def increment_counter():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE counter SET value = value + 1 WHERE id = 1 RETURNING value")
    value = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()
    return value


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return {"id": row[0], "username": row[1], "password_hash": row[2]}
    return None


def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id", (username, password_hash))
        user_id = cursor.fetchone()[0]
        conn.commit()
        return {"id": user_id, "username": username}
    except psycopg2.IntegrityError:
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()