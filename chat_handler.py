from telegram import Update
from telegram.ext import ContextTypes
from config import openai_client

async def chat(update: Update, context: ContextTypes):
    if not context.user_data.get('need_chat', True):
        return
        
    user_input = update.message.text
    prompt = '''You are a professional assistant that helps users purchase car insurance via a Telegram bot.
                Your job is to guide them through the process clearly and politely.
                Try to change any non related to insurence subject to buying car insurance.
                Encourage users to click 'buy insurance' button or write /buy to start insurance purchasing.'''
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Помилка при запиті до OpenAI: {e}"

    await update.message.reply_text(reply)