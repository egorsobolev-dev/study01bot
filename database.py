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
        
        # Таблица заказов (без file_paths для совместимости)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                work_type TEXT,
                description TEXT,
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

def save_order(user_id, work_type, description):
    """Сохранение заказа в базу данных"""
    try:
        conn = sqlite3.connect('academic_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (user_id, work_type, description, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, work_type, description, 'new', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Заказ #{order_id} сохранен для пользователя {user_id}")
        return order_id
        
    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении заказа: {e}")
        if 'conn' in locals():
            conn.close()
        return None