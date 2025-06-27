import os
import mysql.connector
from mysql.connector import pooling, Error

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "harinipanigrahi11")
DB_NAME = os.getenv("DB_NAME", "finance_tracker")

# Step 1: Create database separately (without using the pool)
def create_database():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.commit()
    except Error as err:
        print("DB-create error:", err)
        raise
    finally:
        cursor.close()
        conn.close()

# Step 2: Then connect with pool using that database
DB_CONFIG = {
    "host":     DB_HOST,
    "user":     DB_USER,
    "password": DB_PASS,
    "database": DB_NAME,
}

pool = pooling.MySQLConnectionPool(
    pool_name="fin_pool",
    pool_size=5,
    **DB_CONFIG
)

def get_db_connection():
    return pool.get_connection()

# Step 3: Create tables
def init_db():
    schema = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        description VARCHAR(255),
        amount DECIMAL(10,2),
        category VARCHAR(50),
        user_id INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for stmt in filter(None, (s.strip() for s in schema.split(";"))):
            cursor.execute(stmt)
        conn.commit()
    except Error as err:
        print("DB-init error:", err)
        raise
    finally:
        cursor.close()
        conn.close()

# Run both steps
if __name__ == "__main__":
    create_database()
    init_db()
