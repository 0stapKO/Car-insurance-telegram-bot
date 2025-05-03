from telegram import Update
from telegram.ext import ContextTypes
from bot.config import openai_client

async def chat(update: Update, context: ContextTypes):
    if not context.user_data.get('need_chat', True):
        return
        
    user_input = update.message.text
    prompt = '''You are a professional assistant that helps users purchase car insurance via a Telegram bot.
                Your job is to guide them through the process clearly and politely.
                Try to change any non related to insurence subject to buying car insurance.
                Encourage users to click 'buy insurance' button or write /buy to start insurance purchasing.'''
    
    try:
        reply = await get_gpt_reply(context, prompt, user_input)
    except Exception as e:
        reply = f"Помилка при запиті до OpenAI: {e}"

    await update.message.reply_text(reply)

async def get_gpt_reply(context, prompt, user_input):
    if 'chat_history' not in context.user_data:
        context.user_data['chat_history'] =  [{"role": "system", "content": prompt}]

    context.user_data["chat_history"].append({"role": "user", "content": user_input})
    response = openai_client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=context.user_data['chat_history']
    )
    reply = response.choices[0].message.content
    context.user_data["chat_history"].append({"role": "assistant", "content": reply})
    return reply

async def get_gpt_reply_without_context(prompt, user_input):
    response = openai_client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content