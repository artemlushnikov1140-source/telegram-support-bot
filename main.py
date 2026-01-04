import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ===== ENV =====
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

waiting_for_message = set()

# ===== FAKE HTTP SERVER (ANTI-SLEEP) =====
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_http_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# ===== BOT LOGIC =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["✉️ Написать"]]
    await update.message.reply_text(
        "Здравствуйте!\n\n"
        "Это бот поддержки.\n"
        "Нажмите «Написать», чтобы отправить сообщение.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    waiting_for_message.add(user_id)

    await update.message.reply_text(
        "✍️ Пожалуйста, напишите Ваше сообщение одним сообщением."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # ===== ADMIN ANSWER =====
    if user.id == ADMIN_ID:
        if update.message.reply_to_message and "ID:" in update.message.reply_to_message.text:
            try:
                target_id = int(update.message.reply_to_message.text.split("ID:")[1].split()[0])
                await context.bot.send_message(
                    chat_id=target_id,
                    text=f"💬 Ответ поддержки:\n\n{update.message.text}",
                )
            except:
                pass
        return

    # ===== USER MESSAGE =====
    if user.id not in waiting_for_message:
        return

    waiting_for_message.remove(user.id)

    text = (
        "📩 Новое сообщение в поддержку\n\n"
        f"👤 @{user.username or 'без_ника'}\n"
        f"🆔 ID: {user.id}\n\n"
        f"{update.message.text}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=text)
    await update.message.reply_text("✅ Сообщение отправлено. Ожидайте ответа.")

# ===== MAIN =====
def main():
    threading.Thread(target=run_http_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^✉️ Написать$"), start_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Support bot is running with anti-sleep")
    app.run_polling()

if __name__ == "__main__":
    main()
