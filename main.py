import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- 1. Web Server Setup (To satisfy Render Free Web Service) ---
web_app = Flask(__name__)

@web_app.route('/')
def health_check():
    return "E11 Lab Telegram Bot is Running Live!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- 2. Telegram Bot Configuration ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "123456789"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    
    keyboard = [
        [
            InlineKeyboardButton("🧪 What is E11 Lab?", url="https://e11lab.com")
        ],
        [
            InlineKeyboardButton("🏦 Recommended Brokers", callback_data="brokers_list")
        ],
        [
            InlineKeyboardButton("🎬 Video Tutorial", url="https://youtube.com/your-tutorial-link")
        ],
        [
            InlineKeyboardButton("📢 Community Group & Channel", url="https://t.me/your_community_link")
        ],
        [
            InlineKeyboardButton("💬 Contact Support Team", url="https://t.me/your_support_username")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        f"👋 **Welcome {user_first_name} to E11 Lab!**\n\n"
        "Your hub for trading systems, broker guides, and community support.\n\n"
        "Select an option below to get started, or send a message directly in this chat to speak with our team:"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "brokers_list":
        broker_keyboard = [
            [InlineKeyboardButton("📈 Goldwell Capital", url="https://your-goldwell-ref-link.com")],
            [InlineKeyboardButton("📈 ComoT", url="https://your-comot-ref-link.com")],
            [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_main")]
        ]
        await query.message.reply_text(
            "🏦 **Official Partner Brokers**\n\nChoose a broker below to create and register your account:",
            reply_markup=InlineKeyboardMarkup(broker_keyboard),
            parse_mode="Markdown"
        )
    elif query.data == "back_to_main":
        await start(update, context)

async def handle_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_chat_id = update.message.chat_id
    
    if sender_chat_id != ADMIN_CHAT_ID:
        await update.message.reply_text("📩 **Message received!** Our team has been notified and will reply to you shortly.")
        await context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=sender_chat_id,
            message_id=update.message.message_id
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🚨 **New Message Alert from {update.effective_user.first_name} (@{update.effective_user.username})**\n\n"
                 "💡 *To reply directly to this user, right-click/long-press the forwarded message above and select 'Reply'.*",
            parse_mode="Markdown"
        )
    elif sender_chat_id == ADMIN_CHAT_ID and update.message.reply_to_message:
        try:
            original_user_id = update.message.reply_to_message.forward_from.id
            await context.bot.copy_message(
                chat_id=original_user_id,
                from_chat_id=ADMIN_CHAT_ID,
                message_id=update.message.message_id
            )
            await update.message.reply_text("✅ Reply delivered successfully!")
        except Exception as e:
            await update.message.reply_text(f"❌ Delivery failed: {e}")

# --- 3. Main Execution Thread ---
if __name__ == '__main__':
    # Start Web Server in a separate background thread
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # Start Telegram Bot Polling
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_messages))
    
    print("E11 Lab Bot & Health Server Running...")
    app.run_polling()
