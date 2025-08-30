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
                description TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица файлов к заказам
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                file_id TEXT,
                file_name TEXT,
                file_type TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (id)
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

def save_order_file(order_id, file_id, file_name, file_type):
    """Сохранение информации о файле к заказу"""
    try:
        conn = sqlite3.connect('academic_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO order_files (order_id, file_id, file_name, file_type, uploaded_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_id, file_id, file_name, file_type, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        file_record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Файл {file_name} сохранен для заказа #{order_id}")
        return file_record_id
        
    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении файла: {e}")
        if 'conn' in locals():
            conn.close()
        return None

def get_order_files(order_id):
    """Получение файлов заказа"""
    try:
        conn = sqlite3.connect('academic_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_id, file_name, file_type, uploaded_at
            FROM order_files 
            WHERE order_id = ?
            ORDER BY uploaded_at DESC
        ''', (order_id,))
        
        files = cursor.fetchall()
        conn.close()
        
        return files
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении файлов: {e}")
        return []