import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ApplicationBuilder
from mindee import Client, PredictResponse, product
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
mindee_client = Client(api_key=os.getenv('MINDEE_API_KEY'))

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hi! My name is BuyACarInsuranceBot. I can help you to buy an incurance for your car.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Here is a list of my commands:')

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stage"] = "passport"
    await update.message.reply_text('First of all you have to send me a picture of your passport.')

async def confirmation_buttons(update: Update, data):
    keyboard = [[KeyboardButton('Confirm data'), KeyboardButton('Send another picture')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text('Please, confirm your data.\n' + data, reply_markup=reply_markup)

async def handle_confirmation(update: Update, context: ContextTypes):
    user_input = update.message.text
    stage = context.user_data.get('stage')

    if stage == 'awaiting_passport_confirmation':
        if user_input == 'Confirm data':
            context.user_data['stage'] = 'plate'
            await update.message.reply_text("Great! Now send a picture of your vehicle plate.", reply_markup=ReplyKeyboardRemove())
        elif user_input == 'Send another picture':
            context.user_data['stage'] = 'passport'
            await update.message.reply_text("Okay, please send the passport photo again.", reply_markup=ReplyKeyboardRemove())

    elif stage == 'awaiting_plate_confirmation':
        if user_input == 'Confirm data':
            context.user_data['stage'] = 'done'
            await update.message.reply_text("Thank you! Your information has been confirmed.", reply_markup=ReplyKeyboardRemove())
        elif user_input == 'Send another picture':
            context.user_data['stage'] = 'plate'
            await update.message.reply_text("Okay, please send the vehicle plate photo again.", reply_markup=ReplyKeyboardRemove())


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stage = context.user_data.get("stage")
    photo = update.message.photo[-1]  # Найбільша якість
    file = await context.bot.get_file(photo.file_id)
    # Завантажуємо фото з Telegram на диск
    file_path = f"temp_photo.jpg"
    await file.download_to_drive(file_path)

    if stage == 'passport':
        data = await handle_passport(file_path, update)
        context.user_data['passport_data'] = data
        context.user_data['stage'] = 'awaiting_passport_confirmation'
        await confirmation_buttons(update, data)
        # await update.message.reply_text('Great! Now send a picture of your vehicle plate.')
    elif stage == 'plate':
        data = await handle_plate(file_path, update)
        context.user_data['plate_data'] = data
        context.user_data['stage'] = 'awaiting_plate_confirmation'
        await confirmation_buttons(update, data)
    else:
        await update.message.reply_text('I don\'t know what that image is')

async def handle_passport(file_path, update):
    # Відправляємо фото в Mindee API
    input_doc = mindee_client.source_from_path(file_path)
    result: PredictResponse = mindee_client.parse(
    product.PassportV1,
    input_doc,
)
    # Прибираємо файл
    os.remove(file_path)
    prediction = result.document.inference.prediction
    print(result.document.inference.prediction.surname.value)
    return f'First name: {str([name.value for name in prediction.given_names]).replace('\'', '')[1:-1]}\nLast name: {prediction.surname.value}\nID: {prediction.id_number.value}'

async def handle_plate(file_path, update):
    with open(file_path, "rb") as f:
        response = requests.post(
            "https://api.platerecognizer.com/v1/plate-reader/",
            files=dict(upload=f),
            headers={'Authorization': 'Token ' + os.getenv('PLATE_RECOGNIZER_TOKEN')}
        )
    os.remove(file_path)
    # Обробка результату
    print(response.json())
    return f'Vehicle plate number: {response.json()['results'][0]['plate']}'


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    if context.user_data.get("stage", "").startswith("awaiting_"):
        print('skip')
        return
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти асистент, який допомагає з автострахуванням."},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Помилка при запиті до OpenAI: {e}"

    await update.message.reply_text(reply)


if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv('BOT_TOKEN')).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("buy", buy_command))

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Обробка кнопок підтвердження
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmation))

    # OpenAI-чат — тільки якщо не чекаємо підтвердження
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat), group=1)


    print("Бот працює з OpenAI!")
    app.run_polling()