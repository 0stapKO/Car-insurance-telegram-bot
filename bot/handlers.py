from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from bot.buttons import data_confirmation_buttons, price_confirmation_buttons
from bot.document_generator import send_policy_document
from bot.commands import buy_command
from bot.chat_handler import chat

# Handle user input from confirmation buttons
async def handle_confirmation(update: Update, context: ContextTypes):
    user_input = update.message.text
    stage = context.user_data.get('stage')

    # If the message is not handled by the current logic, pass it to GPT
    context.user_data['need_chat'] = False
    
    if stage == 'start':
        if user_input == 'Buy Insurance':
            await buy_command(update, context)
        else:
            context.user_data['need_chat'] = True
        
    elif stage == 'awaiting_passport_confirmation':
        if user_input == 'Confirm data':
            context.user_data['stage'] = 'plate'
            await update.message.reply_text('Great! Now send a picture of your vehicle plate.', reply_markup=ReplyKeyboardRemove())
        elif user_input == 'Send another picture':
            context.user_data['stage'] = 'passport'
            await update.message.reply_text('Okay, please send the passport photo again.', reply_markup=ReplyKeyboardRemove())
        else:
            context.user_data['need_chat'] = True

    elif stage == 'awaiting_plate_confirmation':
        if user_input == 'Confirm data':
            context.user_data['stage'] = 'price_confirmation'
            await price_confirmation_buttons(update, context)
        elif user_input == 'Send another picture':
            context.user_data['stage'] = 'plate'
            await update.message.reply_text('Okay, please send the plate photo again.', reply_markup=ReplyKeyboardRemove())
        else:
            context.user_data['need_chat'] = True

    elif stage == 'price_confirmation':
        if user_input == 'Buy insurance':
            context.user_data['stage'] = 'start'
            await send_policy_document(update, context.user_data)
            await update.message.reply_text('Here\'s your insurance policy.\nThanks for choosing BuyACarInsuranceBot!', reply_markup=ReplyKeyboardRemove())
        elif user_input == 'Cancel':
            context.user_data['stage'] = 'decline'
            reply = await chat(update, context)
            await update.message.reply_text(reply, reply_markup=ReplyKeyboardRemove())
            context.user_data['stage'] = 'start'
        else:
            context.user_data['need_chat'] = True

    else:
        context.user_data['need_chat'] = True

# Handle uploaded photos (passport or plate), parse them and ask for confirmation
async def handle_photo(update: Update, context: ContextTypes):
    stage = context.user_data.get('stage')
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = 'additional/temp_photo.jpg'
    await file.download_to_drive(file_path)
    
    if stage == 'passport':
        from bot.photo_handler import handle_passport
        try:
            data = await handle_passport(file_path, update)
        except ValueError as e:
            await update.message.reply_text(str(e)+'\nPlease take another photo of your passport.')
            return
        context.user_data['passport_data'] = data
        context.user_data['stage'] = 'awaiting_passport_confirmation'
        await data_confirmation_buttons(update, data)
    elif stage == 'plate':
        from bot.photo_handler import handle_plate
        try:
            data = await handle_plate(file_path, update)
        except ValueError as e:
            await update.message.reply_text(str(e)+'\nPlease take another photo of your vehicle\'s plate.')
            return
        context.user_data['plate_data'] = data
        context.user_data['stage'] = 'awaiting_plate_confirmation'
        await data_confirmation_buttons(update, data)
    else:
        reply = await chat(update, context)
        await update.message.reply_text(reply)