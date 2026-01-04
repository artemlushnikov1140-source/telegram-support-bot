import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("7891053844:AAGu0S7w_YmkFcvPigH4cJ-lTExySck6OJ8")
ADMIN_ID = int(os.getenv("7363981707"))

waiting_for_message = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["✉️ Написать"]]
    await update.message.reply_text(
        "Привет! Это поддержка.\n\nНажми «Написать», чтобы отправить сообщение.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waiting_for_message.add(update.message.from_user.id)
    await update.message.reply_text("✍️ Введите ваше сообщение и отправьте его.")

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

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

if __name__ == "__main__":
    main()