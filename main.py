# main.py
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from handlers import start, new_order, help_command
from database import create_tables

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def main():
    # Создание таблиц БД
    create_tables()
    
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("new_order", new_order))
    application.add_handler(CommandHandler("help", help_command))
    
    # Запуск бота
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())


