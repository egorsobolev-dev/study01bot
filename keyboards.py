# Добавить в handlers.py
from telegram.ext import ConversationHandler

# Константы для состояний разговора
WORK_TYPE, SUBJECT, TOPIC, PAGES, DEADLINE, DESCRIPTION = range(6)

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    work_type = query.data.split('_')[1]  # Извлекаем тип работы
    
    context.user_data['work_type'] = work_type
    
    await query.edit_message_text(
        f"Тип работы: {work_type}\n\n"
        "Укажите предмет (например: История, Математика):"
    )
    
    return SUBJECT

async def get_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['subject'] = update.message.text
    
    await update.message.reply_text(
        "Укажите тему работы:"
    )
    
    return TOPIC

async def get_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['topic'] = update.message.text
    
    await update.message.reply_text(
        "Укажите количество страниц:"
    )
    
    return PAGES

# Продолжить для остальных шагов...