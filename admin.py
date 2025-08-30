# admin.py (расширенная версия)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import sqlite3

ADMIN_IDS = [781822611]

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать заказы с возможностью детального просмотра"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет доступа к этой команде")
        return
    
    conn = sqlite3.connect('academic_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.id, u.first_name, o.work_type, o.status, o.created_at
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        ORDER BY o.created_at DESC 
        LIMIT 10
    ''')
    
    orders = cursor.fetchall()
    conn.close()
    
    if not orders:
        await update.message.reply_text("Новых заказов нет")
        return
    
    text = "📋 Заказы (нажмите для деталей):\n\n"
    keyboard = []
    
    for order in orders:
        order_id, name, work_type, status, created_at = order
        text += f"#{order_id} - {name} ({work_type})\n"
        keyboard.append([InlineKeyboardButton(
            f"📋 Заказ #{order_id}", 
            callback_data=f'order_details_{order_id}'
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ответ клиенту через команду"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет доступа к этой команде")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "📧 Использование: /reply USER_ID текст сообщения\n\n"
            "Пример:\n"
            "/reply 7671242267 Здравствуйте! Ваш заказ принят в работу. Стоимость 3000 руб."
        )
        return
    
    try:
        user_id = int(args[0])
        message_text = " ".join(args[1:])
        
        # Отправка сообщения клиенту
        await context.bot.send_message(
            user_id, 
            f"💬 Сообщение от администратора:\n\n{message_text}"
        )
        
        # Подтверждение админу
        await update.message.reply_text(f"✅ Сообщение отправлено пользователю {user_id}")
        
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID пользователя")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка отправки: {e}")