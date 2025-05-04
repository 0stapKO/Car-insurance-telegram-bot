from bot.config import openai_client

async def get_openai_reply(context, user_input, extra_context=None):
    # Initialize chat history if it doesn't exist in user data
    if 'chat_history' not in context.user_data:
        context.user_data['chat_history'] = [
            {'role': 'system', 'content': '''You are a car insurance assistant. Help users buy insurance. 
            If they send a photo, try to interpret it and confirm extracted data. Be polite and proactive.
            After receiving a photo ask the user if the data you extracted is valid, if not, ask the user to take another photo.
            Wait for the user to confirm the data and then ask to send the next photo.
            Don't ask the user to send the next photo if they haven't confirmed the previous one yet.
            Only after receiving and confirming the photos of passport and license plate tell the user that the estimated price for their insurance is 100 USD and ask them if they are ready to do a purchase.
            If user disagrees to the price apologise and explain that this is the only available price.'''}
        ]

    msg = user_input

    # If there is extra context (e.g., extracted info from image), append it to the message
    if extra_context:
        msg += f"\n[Extracted data: {extra_context}]"
        context.user_data.update(extra_context)

     # Add the user's message to the chat history
    context.user_data['chat_history'].append({'role': 'user', 'content': msg})

    response = openai_client.chat.completions.create(
        model='gpt-4.1-nano',
        messages=context.user_data['chat_history']
    )

    reply = response.choices[0].message.content

    # Add the gpt's reply to the chat history
    context.user_data['chat_history'].append({'role': 'assistant', 'content': reply})
    return reply
