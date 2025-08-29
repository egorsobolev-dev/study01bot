# handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import sqlite3

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Сохранение пользователя в БД
    conn = sqlite3.connect('academic_bot.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
        (user.id, user.username, user.first_name)
    )
    conn.commit()
    conn.close()
    
    welcome_text = f"""
Добро пожаловать, {user.first_name}! 👋

Я бот для приема заказов на академические работы.

Могу помочь с:
📚 Курсовыми работами
🎓 Дипломными проектами
📝 Рефератами и эссе
📊 Презентациями

Используйте /new_order для создания заказа
    """
    
    keyboard = [
        [InlineKeyboardButton("📝 Новый заказ", callback_data='new_order')],
        [InlineKeyboardButton("📋 Мои заказы", callback_data='my_orders')],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 Курсовая работа", callback_data='type_coursework')],
        [InlineKeyboardButton("🎓 Дипломная работа", callback_data='type_diploma')],
        [InlineKeyboardButton("📝 Реферат", callback_data='type_essay')],
        [InlineKeyboardButton("📊 Презентация", callback_data='type_presentation')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Определяем источник - команда или callback
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(
            "Выберите тип работы:", 
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Выберите тип работы:", 
            reply_markup=reply_markup
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):    
    """Обработчик команды /help"""  
    help_text = """
🤖 Доступные команды:

/start - Начать работу с ботом
/help - Показать это сообщение
/new_order - Создать новый заказ

📚 Типы работ:
- Курсовые работы
- Дипломные проекты  
- Рефераты и эссе
- Презентации

📧 Для связи с администратором напишите в этот чат.
    """
    
    # Определяем источник - команда или callback
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(help_text)
    else:
        await update.message.reply_text(help_text)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    # Создаем новый объект Update для callback
    callback_update = Update(
        update_id=update.update_id,
        callback_query=query
    )
    
    if query.data == 'new_order':
        await new_order(callback_update, context)
    elif query.data == 'help':
        await help_command(callback_update, context)
    elif query.data == 'my_orders':
        await query.edit_message_text("📋 Функция 'Мои заказы' в разработке...")
    elif query.data.startswith('type_'):
        work_type = query.data.replace('type_', '').replace('_', ' ').title()
        await query.edit_message_text(f"Вы выбрали: {work_type}\n\n🚧 Форма заказа в разработке...")
    else:
        await query.edit_message_text("Неизвестная команда")