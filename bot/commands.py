from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hi! My name is BuyACarInsuranceBot. I can help you to buy an insurance for your car.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Here is a list of my commands:')

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stage"] = "passport"
    await update.message.reply_text('First of all you have to send me a picture of your passport.')