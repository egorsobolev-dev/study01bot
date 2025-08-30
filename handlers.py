# handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import sqlite3
import logging
from database import save_order
from admin import ADMIN_IDS

logger = logging.getLogger(__name__)

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
    
    # Очищаем контекст пользователя при старте
    context.user_data.clear()
    
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
    
    # Добавляем кнопку администратора если пользователь админ
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("👨‍💼 Админ-панель", callback_data='admin_panel')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Очищаем предыдущий контекст
    context.user_data.clear()
    
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
    elif query.data == 'admin_panel':
        # Проверяем права администратора
        if query.from_user.id in ADMIN_IDS:
            keyboard = [
                [InlineKeyboardButton("📋 Посмотреть заказы", callback_data='view_orders')],
                [InlineKeyboardButton("📊 Статистика", callback_data='statistics')],
                [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("👨‍💼 Админ-панель:", reply_markup=reply_markup)
        else:
            await query.edit_message_text("❌ У вас нет прав администратора")
    elif query.data == 'view_orders':
        if query.from_user.id in ADMIN_IDS:
            await show_admin_orders(query)
        else:
            await query.edit_message_text("❌ У вас нет прав администратора")
    elif query.data == 'back_to_main':
        # Возвращаемся к главному меню
        user = query.from_user
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
        
        if user.id in ADMIN_IDS:
            keyboard.append([InlineKeyboardButton("👨‍💼 Админ-панель", callback_data='admin_panel')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(welcome_text, reply_markup=reply_markup)
    elif query.data.startswith('type_'):
        work_type_map = {
            'type_coursework': 'Курсовая работа',
            'type_diploma': 'Дипломная работа', 
            'type_essay': 'Реферат',
            'type_presentation': 'Презентация'
        }
        
        work_type = work_type_map.get(query.data, 'Неизвестный тип')
        
        # Сохраняем выбранный тип работы в контексте пользователя
        context.user_data['selected_work_type'] = work_type
        context.user_data['waiting_for_description'] = True
        context.user_data['user_id'] = query.from_user.id
        
        await query.edit_message_text(
            f"Вы выбрали: {work_type}\n\n"
            "📝 Отправьте максимально подробное описание работы и приложите все имеющиеся материалы/референсы.\n\n"
            "Укажите:\n"
            "• Тему работы\n"
            "• Объем (количество страниц)\n"
            "• Сроки выполнения\n"
            "• Особые требования\n"
            "• Методические указания (если есть)\n\n"
            "После описания можете прикрепить файлы с дополнительными материалами.\n\n"
            "Для отмены используйте /start"
        )
    else:
        await query.edit_message_text("Неизвестная команда")

async def handle_order_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик описания заказа"""
    
    # Проверяем, ожидается ли описание от этого пользователя
    if not context.user_data.get('waiting_for_description'):
        return  # Игнорируем сообщение если не ожидаем описание
    
    user = update.effective_user
    work_type = context.user_data.get('selected_work_type', 'Не указан')
    description = update.message.text
    
    # Сохраняем заказ в базу данных
    order_id = save_order(user.id, work_type, description)
    
    if order_id:
        # Отправляем подтверждение пользователю
        await update.message.reply_text(
            f"✅ Ваш заказ #{order_id} принят!\n\n"
            f"Тип работы: {work_type}\n"
            f"Описание: {description[:100]}...\n\n"
            "📞 С вами свяжется администратор для уточнения деталей и расчета стоимости."
        )
        
        # Уведомление администратору
        await send_admin_notification(context, {
            'id': order_id,
            'user_id': user.id,
            'user_name': user.first_name,
            'username': f"@{user.username}" if user.username else "Без username",
            'work_type': work_type,
            'description': description
        })
        
        # Очищаем контекст пользователя
        context.user_data.clear()
        
    else:
        await update.message.reply_text(
            "❌ Произошла ошибка при сохранении заказа. Попробуйте еще раз или обратитесь к администратору."
        )

async def handle_order_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик файлов к заказу"""
    
    # Если пользователь отправил файл после создания заказа
    if context.user_data.get('waiting_for_description'):
        file_name = "Неизвестный файл"
        if update.message.document:
            file_name = update.message.document.file_name
        elif update.message.photo:
            file_name = "Изображение"
        
        await update.message.reply_text(
            f"📎 Файл '{file_name}' получен!\n\n"
            "Теперь отправьте текстовое описание работы."
        )

async def send_admin_notification(context: ContextTypes, order_data):
    """Отправка уведомления администратору о новом заказе"""
    
    admin_message = f"""
🆕 НОВЫЙ ЗАКАЗ #{order_data['id']}

👤 Клиент: {order_data['user_name']} ({order_data['username']})
🆔 ID: {order_data['user_id']}
📚 Тип работы: {order_data['work_type']}

📝 Описание:
{order_data['description']}

💬 Для ответа клиенту используйте его ID: {order_data['user_id']}
    """
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(admin_id, admin_message)
            logger.info(f"Уведомление о заказе #{order_data['id']} отправлено админу {admin_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления админу {admin_id}: {e}")

async def show_admin_orders(query):
    """Показать заказы администратору"""
    try:
        conn = sqlite3.connect('academic_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id, u.first_name, o.work_type, o.description, o.status, o.created_at
            FROM orders o 
            JOIN users u ON o.user_id = u.user_id 
            ORDER BY o.created_at DESC 
            LIMIT 10
        ''')
        
        orders = cursor.fetchall()
        conn.close()
        
        if not orders:
            await query.edit_message_text("📋 Новых заказов нет")
            return
        
        text = "📋 Последние заказы:\n\n"
        for order in orders:
            order_id, name, work_type, description, status, created_at = order
            text += f"#{order_id} - {name}\n"
            text += f"Тип: {work_type}\n"
            text += f"Описание: {description[:50]}...\n"
            text += f"Статус: {status}\n"
            text += f"Дата: {created_at}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='admin_panel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка при показе заказов: {e}")
        await query.edit_message_text("❌ Ошибка при загрузке заказов")