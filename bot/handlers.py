from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from bot.chat_handler import get_openai_reply
from bot.photo_handler import parse_photo_data
from bot.document_generator import send_policy_document

async def handle_message_or_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = '' # Will store the user's message or a placeholder like "[Photo Uploaded]"
    extra_context = {} # Holds extracted data from photos (passport/plate)

    # Handle photo input
    if update.message and update.message.photo:
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_path = 'additional/temp.jpg'
        await file.download_to_drive(file_path)

        # Extract data from the image using Mindee
        extracted_data = await parse_photo_data(file_path, context)

        # If returned nothing or an error
        if not extracted_data or 'Error' in extracted_data:
            await update.message.reply_text("Couldn\'t recognize the data from the photo. Please send another one.")
            return

        # Store extracted data in user context
        if 'First name' in extracted_data:
            context.user_data['passport_data'] = extracted_data
            extra_context = {'passport_data': extracted_data}
        elif 'Vehicle license plate' in extracted_data:
            context.user_data['plate_data'] = extracted_data
            extra_context = {'plate_data': extracted_data}

        user_input = '[Photo Uploaded]'
        reply = await get_openai_reply(context, user_input, extra_context)

        # Show "Yes" button to confirm data
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("Yes")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await update.message.reply_text(reply, reply_markup=keyboard)

    # Handle text input
    elif update.message and update.message.text:
        user_input = update.message.text.lower()

        if user_input == 'yes':
            # Passport data confirmation
            if 'passport_data' in context.user_data and not context.user_data.get('confirmed_passport'):
                context.user_data['confirmed_passport'] = True
                if context.user_data.get('confirmed_plate'):
                    keyboard = ReplyKeyboardMarkup(
                        [[KeyboardButton("Yes")]],
                        resize_keyboard=True,
                        one_time_keyboard=True
                    )
                    await update.message.reply_text(
                        "The estimated price of incurance is 100 USD. If you agree click 'Yes'.",
                        reply_markup=keyboard
                    )
                else:
                    await update.message.reply_text("Passport data confirmed. Now send a photo of you vehicle's license plate.")
                return

            # Plate number confirmation
            if 'plate_data' in context.user_data and not context.user_data.get('confirmed_plate'):
                context.user_data['confirmed_plate'] = True
                if context.user_data.get('confirmed_passport'):
                    keyboard = ReplyKeyboardMarkup(
                        [[KeyboardButton("Yes")]],
                        resize_keyboard=True,
                        one_time_keyboard=True
                    )
                    await update.message.reply_text(
                        "The estimated price of incurance is 100 USD. If you agree click 'Yes'.",
                        reply_markup=keyboard
                    )
                else:
                    await update.message.reply_text("License plate confirmed. Now send a photo of you passport.")
                return

            # Price confirmation
            if context.user_data.get('confirmed_passport') and context.user_data.get('confirmed_plate') and not context.user_data.get('price_confirmed'):
                context.user_data['price_confirmed'] = True
                await update.message.reply_text("Generating insurance policy... ")
                await send_policy_document(update, context.user_data)
                await update.message.reply_text("Thanks for using BuyACarInsuranceBot!")
                return

        reply = await get_openai_reply(context, user_input)
        await update.message.reply_text(reply)
