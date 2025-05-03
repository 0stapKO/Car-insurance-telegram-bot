from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

async def data_confirmation_buttons(update: Update, data):
    keyboard = [[KeyboardButton('Confirm data'), KeyboardButton('Send another picture')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    data_to_confirm = '\n'.join([f"{key}: {data[key]}" for key in data])
    await update.message.reply_text(f'Please, confirm your data.\n{data_to_confirm}', reply_markup=reply_markup)

async def price_confirmation_buttons(update: Update, context):
    keyboard = [[KeyboardButton('Buy insurance'), KeyboardButton('Cancel')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Thank you! The fixed price for the insurance is estimated to be 100$", reply_markup=reply_markup)