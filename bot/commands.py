from telegram import Update
from telegram.ext import ContextTypes

# /start command handler, reset bot
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text('Hi! My name is BuyACarInsuranceBot. I can help you to buy an insurance for your car.')

# /help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I\'m here to help you buy an incurance for your vehicle. For I will need your passport data and your vehicle\'s license plate. In the end you will receive an insurance policy document.')
