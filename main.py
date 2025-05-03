from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from commands import start_command, help_command, buy_command
from handlers import handle_confirmation, handle_photo
from chat_handler import chat

if __name__ == '__main__':
    from config import BOT_TOKEN
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Реєстрація обробників
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("buy", buy_command))
    
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmation))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat), group=1)

    print("Бот працює з OpenAI!")
    app.run_polling()