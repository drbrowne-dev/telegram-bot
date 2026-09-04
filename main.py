import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "123456789"))  # Replace 123456789 with your Telegram ID from @userinfobot

# 1. Welcome Message with Updated Button Hierarchy
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    
    keyboard = [
        [
            # Link directly to your website
            InlineKeyboardButton("🧪 What is E11 Lab?", url="https://e11lab.com")
        ],
        [
            # Sub-menu button for supported brokers
            InlineKeyboardButton("🏦 Recommended Brokers", callback_data="brokers_list")
        ],
        [
            # Link directly to your YouTube Video Tutorial
            InlineKeyboardButton("🎬 Video Tutorial", url="https://youtube.com/your-tutorial-link")
        ],
        [
            # Community Invite Link
            InlineKeyboardButton("📢 Community Group & Channel", url="https://t.me/your_community_link")
        ],
        [
            # Direct Link to Support Team Chat/ID
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

# 2. Callback Handler for Brokers Sub-menu
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "brokers_list":
        # Interactive buttons listing the specific broker registration links
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
        # Re-trigger start menu view
        await start(update, context)

# 3. Live Support Forwarder & Manual Reply Logic
async def handle_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_chat_id = update.message.chat_id
    
    # Forward user text message to Admin
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

    # Admin replies back to user via the bot
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

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_messages))
    
    print("E11 Lab Bot Running...")
    app.run_polling()
