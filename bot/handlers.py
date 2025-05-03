from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, MessageHandler, filters
from bot.confirmation import data_confirmation_buttons, price_confirmation_buttons
from bot.document_generator import send_policy_document


async def handle_confirmation(update: Update, context: ContextTypes):
    user_input = update.message.text
    stage = context.user_data.get('stage')
    context.user_data['need_chat'] = False
    
    if stage == 'awaiting_passport_confirmation':
        if user_input == 'Confirm data':
            context.user_data['stage'] = 'plate'
            await update.message.reply_text("Great! Now send a picture of your vehicle plate.", reply_markup=ReplyKeyboardRemove())
        elif user_input == 'Send another picture':
            context.user_data['stage'] = 'passport'
            await update.message.reply_text("Okay, please send the passport photo again.", reply_markup=ReplyKeyboardRemove())

    elif stage == 'awaiting_plate_confirmation':
        if user_input == 'Confirm data':
            context.user_data['stage'] = 'price_confirmation'
            await price_confirmation_buttons(update, context)
        elif user_input == 'Send another picture':
            context.user_data['stage'] = 'plate'
            await update.message.reply_text("Okay, please send the plate photo again.", reply_markup=ReplyKeyboardRemove())

    elif stage == 'price_confirmation':
        context.user_data['stage'] = 'start'
        if user_input == 'Buy insurance':
            await send_policy_document(update, context.user_data)
            await update.message.reply_text("Here's your insurance policy.\nThanks for choosing BuyACarInsuranceBot!", reply_markup=ReplyKeyboardRemove())
        elif user_input == 'Cancel':
            await update.message.reply_text("Sorry. 100$ is the only available price.", reply_markup=ReplyKeyboardRemove())
    else:
        context.user_data['need_chat'] = True

async def handle_photo(update: Update, context: ContextTypes):
    stage = context.user_data.get("stage")
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = "additional/temp_photo.jpg"
    await file.download_to_drive(file_path)
    
    if stage == 'passport':
        from bot.photo_handler import handle_passport
        data = await handle_passport(file_path, update)
        context.user_data['passport_data'] = data
        context.user_data['stage'] = 'awaiting_passport_confirmation'
        await data_confirmation_buttons(update, data)
    elif stage == 'plate':
        from bot.photo_handler import handle_plate
        data = await handle_plate(file_path, update)
        context.user_data['plate_data'] = data
        context.user_data['stage'] = 'awaiting_plate_confirmation'
        await data_confirmation_buttons(update, data)
    else:
        await update.message.reply_text('I don\'t know what that image is')