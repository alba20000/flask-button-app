import os
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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
    """Initialize database using migrations instead of hardcoded schema.
    
    This function now only ensures the database is accessible.
    Schema changes should be done via Alembic migrations.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Just test the connection - migrations handle schema
    cursor.execute("SELECT 1")
    
    cursor.close()
    conn.close()


def get_counter(user_id):
    """Get counter value for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM counter WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    
    if row is None:
        # Create counter for this user if it doesn't exist
        cursor.execute("INSERT INTO counter (user_id, value) VALUES (%s, 0) RETURNING value", (user_id,))
        value = cursor.fetchone()[0]
    else:
        value = row[0]

    cursor.close()
    conn.close()
    return value


def increment_counter(user_id):
    """Increment counter for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()

    # Ensure counter exists for user
    cursor.execute("""
        INSERT INTO counter (user_id, value) 
        VALUES (%s, 0) 
        ON CONFLICT DO NOTHING
    """, (user_id,))
    
    cursor.execute("UPDATE counter SET value = value + 1 WHERE user_id = %s RETURNING value", (user_id,))
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


def get_user_by_id(user_id):
    """Get user by ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return {"id": row[0], "username": row[1]}
    return None


def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (%s, %s, %s) RETURNING id", 
            (username, password_hash, datetime.now())
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        return {"id": user_id, "username": username}
    except psycopg2.IntegrityError:
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()


def get_all_users():
    """Get all users for management purposes."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, created_at, is_active FROM users ORDER BY created_at DESC")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [{"id": row[0], "username": row[1], "created_at": row[2], "is_active": row[3]} for row in rows]


def deactivate_user(user_id):
    """Deactivate a user account."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE users SET is_active = false WHERE id = %s", (user_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def activate_user(user_id):
    """Activate a user account."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE users SET is_active = true WHERE id = %s", (user_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def delete_user(user_id):
    """Delete a user account."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()