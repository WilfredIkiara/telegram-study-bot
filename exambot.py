import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
from aiohttp import web
import threading

# ===== CONFIGURATION =====
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROUP_CHAT_ID = os.environ.get('GROUP_CHAT_ID', '@YourGroupName')

# ===== HEALTH CHECK SERVER =====
async def health_check(request):
    return web.Response(text="Bot is running!")

def start_health_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    port = int(os.environ.get('PORT', 8080))
    web.run_app(app, host='0.0.0.0', port=port)

# ===== YOUR EXISTING BOT CODE =====
OFFICIAL_MESSAGES = {
    # ... your existing messages ...
}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"🎓 **Exam Study Bot Activated!**\n\nHello {user.first_name}! I'm here to help manage the study group."
    await update.message.reply_text(welcome_text)

# ... REST OF YOUR EXISTING BOT FUNCTIONS ...

def main():
    # Verify token is available
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN environment variable is not set!")
        print("💡 Please set it in Render dashboard environment variables")
        return
    
    # Start health server in a separate thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Create and start bot application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("rules", rules_command))
    application.add_handler(CommandHandler("motivate", motivate_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    
    # Scheduled messages task
    async def scheduled_task():
        while True:
            try:
                await send_scheduled_message(application)
                await asyncio.sleep(1800)  # 30 minutes
            except Exception as e:
                print(f"Scheduled task error: {e}")
                await asyncio.sleep(60)
    
    # Post-init setup
    async def post_startup(application):
        print("🎓 Exam Study Bot is running!")
        print(f"🤖 Managing group: {GROUP_CHAT_ID}")
        asyncio.create_task(scheduled_task())
    
    application.post_init = post_startup
    
    print("🚀 Starting Exam Study Bot...")
    application.run_polling()

if __name__ == '__main__':
    main()