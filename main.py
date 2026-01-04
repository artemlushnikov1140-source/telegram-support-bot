import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Берём значения из Render (Environment Variables)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Храним состояние: кто сейчас пишет сообщение
waiting_for_message = set()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["✉️ Написать"]]
    await update.message.reply_text(
        "Привет! Это поддержка.\n\nНажми «Написать», чтобы отправить сообщение.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# Нажали кнопку "Написать"
async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    waiting_for_message.add(user_id)
    await update.message.reply_text("✍️ Введите ваше сообщение и отправьте его.")

# Пользователь прислал текст
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # если это админ — обрабатываем отдельно
    if user.id == ADMIN_ID:
        if update.message.reply_to_message:
            original = update.message.reply_to_message.text
            if "ID:" in original:
                target_id = int(original.split("ID:")[1].split("\n")[0])
                await context.bot.send_message(
                    chat_id=target_id,
                    text=f"💬 Ответ от поддержки:\n{update.message.text}"
                )
        return

    # если пользователь не нажал "Написать" — игнор
    if user.id not in waiting_for_message:
        return

    waiting_for_message.remove(user.id)

    text = (
        f"📩 Новое сообщение\n"
        f"👤 @{user.username or 'без_ника'}\n"
        f"🆔 ID: {user.id}\n\n"
        f"{update.message.text}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=text)
    await update.message.reply_text("✅ Сообщение отправлено. Ожидайте ответа.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^✉️ Написать$"), start_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

    print("Бот запущен")
    app.run_polling()

if name == "__main__":
    main()
