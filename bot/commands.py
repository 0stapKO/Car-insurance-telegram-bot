from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

# Set stage to start and greet the user
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['stage'] = 'start'
    await update.message.reply_text('Hi! My name is BuyACarInsuranceBot. I can help you to buy an insurance for your car.')

# Show available commands
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Here is a list of my commands:\n/buy - start the purchase\n/help - show a list of commands')

# Start the process, move to next step, hide 'Buy Insurance' button
async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['stage'] = 'passport'
    await update.message.reply_text('First of all you have to send me a picture of your passport.', reply_markup=ReplyKeyboardRemove())