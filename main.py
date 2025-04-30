import os
import requests
from telegram import Update
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



async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stage = context.user_data.get("stage")
    photo = update.message.photo[-1]  # Найбільша якість
    file = await context.bot.get_file(photo.file_id)
    # Завантажуємо фото з Telegram на диск
    file_path = f"temp_photo.jpg"
    await file.download_to_drive(file_path)

    if stage == 'passport':
        await handle_passport(file_path, update)

        context.user_data['stage'] = 'plate'
        await update.message.reply_text('Great! Now send a picture of your vehicle plate.')
    elif stage == 'plate':
        await handle_plate(file_path, update)
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
    await update.message.reply_text(f'Please confirm your data.\nFirst name: {str([name.value for name in prediction.given_names]).replace('\'', '')[1:-1]}\nLast name: {prediction.surname.value}\nID: {prediction.id_number.value}')

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
    await update.message.reply_text(f'Please confirm your data.\nVehicle plate number: {response.json()['results'][0]['plate']}')


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
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

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Бот працює з OpenAI!")
    app.run_polling()