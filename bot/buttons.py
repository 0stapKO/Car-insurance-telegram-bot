from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from bot.chat_handler import chat

# Show buttons to confirm data or send another picture
async def data_confirmation_buttons(update: Update, data):
    keyboard = [[KeyboardButton('Confirm data'), KeyboardButton('Send another picture')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    data_to_confirm = '\n'.join([f"{key}: {data[key]}" for key in data])
    await update.message.reply_text(f'Please, confirm your data.\n{data_to_confirm}', reply_markup=reply_markup)

# Show buttons to confirm the price
async def price_confirmation_buttons(update: Update, context: ContextTypes):
    keyboard = [[KeyboardButton('Buy insurance'), KeyboardButton('Cancel')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text('Thank you! The fixed price for the insurance is estimated to be 100$', reply_markup=reply_markup)

# Show the start button "Buy Insurance"
async def buy_button(update: Update, context: ContextTypes):
    if not context.user_data.get('need_chat', True):
        return
    keyboard = [[KeyboardButton('Buy Insurance')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    reply = await chat(update, context)
    if context.user_data['stage'] == 'start':
        await update.message.reply_text(reply, reply_markup=reply_markup)
    else:
        await update.message.reply_text(reply)
    