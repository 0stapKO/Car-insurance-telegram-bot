from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.commands import start_command, help_command, buy_command
from bot.handlers import handle_confirmation, handle_photo
from bot.buttons import buy_button
from bot.config import BOT_TOKEN

if __name__ == '__main__':
    
    # Build the Telegram bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('buy', buy_command))
    
    # Handle photos (passport or plate)
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Handle text messages for confirmation buttons
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmation))
    # Handle messages with "Buy Insurance" button
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buy_button), group=1)

    app.run_polling()