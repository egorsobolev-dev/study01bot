# admin.py
ADMIN_IDS = [781822611]  # ID администраторов

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет доступа к этой команде")
        return
    
    conn = sqlite3.connect('academic_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.id, u.first_name, o.work_type, o.topic, o.status 
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
    
    text = "📋 Последние заказы:\n\n"
    for order in orders:
        text += f"#{order[0]} - {order[1]}\n"
        text += f"Тип: {order[2]}\n"
        text += f"Тема: {order[3][:50]}...\n"
        text += f"Статус: {order[4]}\n\n"
    
    await update.message.reply_text(text)
