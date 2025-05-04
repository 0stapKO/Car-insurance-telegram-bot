from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.commands import start_command, help_command
from bot.handlers import handle_message_or_photo
from bot.config import BOT_TOKEN

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Сommand handlers for '/start' and '/help'
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    # Message handler that responds to text or photo messages
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO & ~filters.COMMAND, handle_message_or_photo))

    app.run_polling()
