from telegram import Update
from telegram.ext import ContextTypes
from bot.config import openai_client

# Interaction through OpenAI
async def chat(update: Update, context: ContextTypes):
    if not 'stage' in context.user_data:
        context.user_data['stage'] = 'start'

    prompt = '''You are a professional assistant that helps users purchase car insurance via a Telegram bot.
                Your job is to guide them through the process clearly and politely.
                Try to change any non related to insurence subject to buying car insurance.'''
    
    user_input = update.message.text or ' '

    # Stage-specific instructions for GPT
    if context.user_data['stage'] == 'passport':
        additional_prompt = '\nEncourage users to send a photo of their passport so that you could proceed a purchase.'
    elif context.user_data['stage'] == 'awaiting_passport_confirmation':
        additional_prompt = '\nThe user has already sent a photo of their passport. Encourage users to check if you got their name and id right. If not, suggest take another photo of the passport.'
    elif context.user_data['stage'] == 'plate':
        additional_prompt = '\nForget about passport. Encourage users to send a photo of their vehicle\'s plate so that you could proceed a purchase.'
    elif context.user_data['stage'] == 'awaiting_plate_confirmation':
        additional_prompt = '\nThe user has already sent a photo of their vehicle\'s plate. Encourage users to check if you got the plate number right. If not, suggest take another photo of the plate.'
    elif context.user_data['stage'] == 'price_confirmation':
        additional_prompt = '\nForget about plate. Remind users that an estimated price for their insurance is 100 USD. Ask if they agree.'
    elif context.user_data['stage'] == 'decline':
        additional_prompt = '\nApologise for having suggesting such a high price (100USD) and explain that this is the only available price.'
    else:
        additional_prompt = '\nEncourage users to click \'Buy Insurance\' button or write /buy to start insurance purchasing.'
    
    try:
        reply = await get_gpt_reply(context, prompt+additional_prompt, user_input)
        return reply
    except Exception:
        return 'Sorry! During connectiong to OpenAI an error occured.'

# Send user message to GPT with chat history
async def get_gpt_reply(context, prompt, user_input):
    if 'chat_history' not in context.user_data:
        context.user_data['chat_history'] =  [{'role': 'system', 'content': prompt}]

    context.user_data['chat_history'][0]['content'] = prompt
    context.user_data['chat_history'].append({'role': 'user', 'content': user_input})

    response = openai_client.chat.completions.create(
        model='gpt-4.1-nano',
        messages=context.user_data['chat_history']
    )
    reply = response.choices[0].message.content
    context.user_data['chat_history'].append({'role': 'assistant', 'content': reply})
    return reply

# Send message to GPT without keeping chat history (for document generation)
async def get_gpt_reply_without_context(prompt, user_input):
    response = openai_client.chat.completions.create(
        model='gpt-4.1-nano',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': user_input}
        ]
    )
    return response.choices[0].message.content