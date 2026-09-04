import os
import threading
from flask import Flask, render_template
from waitress import serve
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# --- 1. Flask Web Server Setup ---
web_app = Flask(__name__)

@web_app.route('/')
def health_check():
    return "E11 Lab Bot is Active!", 200

# Mini App route (serves templates/mini_app.html)
@web_app.route('/app')
def serve_mini_app():
    return render_template('mini_app.html')

def start_flask_server():
    port = int(os.environ.get("PORT", 8080))
    serve(web_app, host="0.0.0.0", port=port)

# --- 2. Environment Variables & Safety Checks ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID_RAW = os.getenv("ADMIN_CHAT_ID", "0")

if not TOKEN:
    print("❌ FATAL: BOT_TOKEN is missing from environment variables!")
    exit(1)

try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID_RAW)
except ValueError:
    print("❌ FATAL: ADMIN_CHAT_ID must be digits only!")
    exit(1)

# --- 3. Telegram Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    
    # Navigation Keyboard with your real Channel and Group links
    keyboard = [
        [InlineKeyboardButton("🧪 What is E11 Lab?", url="https://e11lab.com")],
        [InlineKeyboardButton("🏦 Recommended Brokers", callback_data="brokers_list")],
        [InlineKeyboardButton("🎬 Video Tutorial", url="https://youtube.com/your-tutorial-link")],
        [InlineKeyboardButton("📢 Market Insight Channel", url="https://t.me/e11lab_TradingDesk_MarketInsight")],
        [InlineKeyboardButton("💬 E11 Lab Community Group", url="https://t.me/E11LabCommunity")],
        [InlineKeyboardButton("💬 Contact Support Team", url="https://t.me/your_support_username")]
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
    
    # Message Routing: Standard User -> Forward to Admin
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
                 "💡 *To reply directly to this user, right-click or long-press the forwarded message above and select 'Reply'.*",
            parse_mode="Markdown"
        )
    # Message Routing: Admin replying to forwarded message -> Send back to User
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

# --- 4. Main Execution ---
if __name__ == "__main__":
    # Start Flask server thread for Render keep-alive and Mini App serving
    threading.Thread(target=start_flask_server, daemon=True).start()

    # Launch Telegram Bot
    print("🚀 E11 Lab Bot initializing...")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_messages))

    # Run polling loop
    app.run_polling(drop_pending_updates=True)
