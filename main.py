# main.py
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import Conflict, NetworkError
from config import BOT_TOKEN
from handlers import start, new_order, help_command, button_handler, handle_order_description, handle_order_files
from admin import admin_orders
from database import create_tables

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Запуск бота"""
    try:
        logger.info("🤖 Запуск бота...")
        
        # Проверка токена
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN не найден!")
            sys.exit(1)
        
        # Создание таблиц БД
        create_tables()
        
        # Создание приложения
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Регистрация обработчиков команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("new_order", new_order))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("admin_orders", admin_orders))
        
        # Регистрация обработчика кнопок
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Обработчики текстовых сообщений и файлов
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_description))
        application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_order_files))
        
        logger.info("✅ Обработчики зарегистрированы")
        logger.info("🚀 Бот запущен и готов к работе!")
        
        # Запуск бота с обработкой ошибок
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True  # Очищает pending обновления при запуске
        )
        
    except Conflict as e:
        logger.error("❌ КОНФЛИКТ: Другой экземпляр бота уже запущен!")
        logger.error("Остановите бота на Railway или закройте другие копии")
        logger.error(f"Детали ошибки: {e}")
        sys.exit(1)
        
    except NetworkError as e:
        logger.error(f"❌ Ошибка сети: {e}")
        logger.error("Проверьте подключение к интернету")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()