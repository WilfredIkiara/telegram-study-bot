import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# ===== CONFIGURATION =====
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROUP_CHAT_ID = os.environ.get('GROUP_CHAT_ID', '@ExamStudyGroupKenya')

# ===== MESSAGE TEMPLATES =====
OFFICIAL_MESSAGES = {
    "welcome": """
🎓 **WELCOME TO EXAM STUDY GROUP!** 🎓

Dear {name}, welcome to our exam preparation community!

📋 **GROUP RULES:**
• Be respectful to all members
• No spam or irrelevant content
• Keep discussions educational
• Share study materials responsibly

💬 **Need help?** Use /help for available commands
    """,

    "study_reminder": """
📚 **STUDY SCHEDULE REMINDER** 📚
━━━━━━━━━━━━━━━━━━━━━━━━

🕒 **Daily Study Time:** 2-3 hours recommended
📖 **Focus Areas:** Key concepts and past papers
👥 **Group Discussions:** Share insights and questions

🎯 **Remember:** Consistent study beats cramming!
    """,

    "motivation": """
🌟 **MOTIVATION & ENCOURAGEMENT** 🌟
━━━━━━━━━━━━━━━━━━━━━━━━

💫 **Today's Message:** BE PATIENT, RELAX, AND REVISE

📚 **Focus Areas:**
• Review key concepts
• Practice past papers
• Engage in group discussions
• Stay calm and confident

🎯 **You've got this!** 💪
    """
}

# ===== BOT COMMANDS =====
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"🎓 **Exam Study Bot Activated!**\n\nHello {user.first_name}! I'm here to help manage the study group. Use /help to see available commands."
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔍 **AVAILABLE COMMANDS:**

/start - Activate the bot
/help - Show this help message
/schedule - Study schedule and tips
/rules - Group rules and guidelines
/motivate - Get study motivation

💬 **AUTO-RESPONSES:**
I automatically respond to: hello, hi, hey, study, exam, help
    """
    await update.message.reply_text(help_text)

async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(OFFICIAL_MESSAGES["study_reminder"])

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_text = """
📋 **GROUP RULES** 📋

1️⃣ **RESPECT ALL MEMBERS** - No harassment
2️⃣ **NO SPAMMING** - Keep messages relevant  
3️⃣ **HELP EACH OTHER** - Share knowledge
4️⃣ **STAY POSITIVE** - Encourage each other
5️⃣ **BE ACTIVE** - Participate in discussions
    """
    await update.message.reply_text(rules_text)

async def motivate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(OFFICIAL_MESSAGES["motivation"])

# ===== AUTO-RESPONSES =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user = update.effective_user
    
    responses = {
        'hello': f"👋 Hello {user.first_name}! Ready to study?",
        'hi': f"👋 Hi {user.first_name}! Use /help for commands.",
        'hey': f"👋 Hey {user.first_name}! Need study tips?",
        'exam': "📚 Focus on understanding concepts, not just memorizing!",
        'study': "📖 Regular study sessions are key to success!",
        'help': "💡 Use /help to see all available commands",
        'thanks': "👍 You're welcome! Keep up the good work!",
        'thank you': "🎓 You're welcome! Stay focused!"
    }
    
    for keyword, response in responses.items():
        if keyword in text:
            await update.message.reply_text(response)
            break

# ===== WELCOME NEW MEMBERS =====
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        welcome_text = OFFICIAL_MESSAGES["welcome"].format(name=member.first_name)
        await update.message.reply_text(welcome_text)

# ===== SCHEDULED MESSAGES =====
async def send_scheduled_message(application):
    try:
        messages = [
            OFFICIAL_MESSAGES["study_reminder"],
            OFFICIAL_MESSAGES["motivation"]
        ]
        
        current_minute = datetime.now().minute
        message_index = (current_minute // 30) % len(messages)
        
        message = messages[message_index]
        await application.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=message
        )
        print(f"✅ Scheduled message sent at {datetime.now()}")
        
    except Exception as e:
        print(f"❌ Error sending scheduled message: {e}")

# ===== MAIN SETUP =====
def main():
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN environment variable is not set!")
        print("💡 Please set it in Render dashboard environment variables")
        return
    
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
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
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