# database.py
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def create_tables():
    try:
        conn = sqlite3.connect('academic_bot.db')
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                work_type TEXT,
                subject TEXT,
                topic TEXT,
                pages INTEGER,
                deadline TEXT,
                description TEXT,
                price REAL,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Таблицы базы данных созданы успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании таблиц БД: {e}")
        raise