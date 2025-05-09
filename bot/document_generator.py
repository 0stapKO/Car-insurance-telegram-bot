from fpdf import FPDF
from datetime import datetime
from bot.config import openai_client
import os

# Generate insurance policy document using GPT and save as PDF
async def generate_policy_document(user_data):
    today = datetime.today().strftime('%B %d, %Y')
    full_name = f'{user_data['passport_data']['First name']} {user_data['passport_data']['Last name']}'
    id = user_data['passport_data']['ID']
    license_plate = user_data['plate_data']['Vehicle license plate']
    
    prompt = f'''You are a virtual insurance assistant. Generate a car insurance policy document for a client named {full_name}, who owns a vehicle with the license plate number {license_plate}.

        The insurance policy costs 100 USD and is valid for 1 year from the issue date. Create a realistic and professional-looking insurance policy text that includes:

        - A unique policy number (you can make one up),
        - The issue date (use today's date),
        - The client's full name,
        - The client's id,
        - The vehicle's license plate number,
        - The total cost: 100 USD,
        - The policy period: 1 year from the issue date,
        - A short paragraph with general insurance terms.

        Output format should be as follows:

        
        INSURANCE POLICY No. [Policy Number]

        Issued on: {today}

        Policyholder's name: {full_name}  
        Policyholder's id: {id}  
        Vehicle License Plate: {license_plate}

        Insured Amount: 100 USD  
        Coverage Period: [Start Date] - [End Date]

        [Brief paragraph describing general insurance coverage terms.]

        Thank you for choosing our insurance services.'''
    
    try:
        response = openai_client.chat.completions.create(
        model='gpt-4.1-nano',
        messages=[
            {'role': 'system', 'content': prompt}
        ]
    )
        response = response.choices[0].message.content
        
        # Generate PDF from GPT response and save as insurance_policy.pdf
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', size=14)
        for line in response.strip().split('\n'):
            pdf.multi_cell(0, 10, line)
        pdf.output('additional/insurance_policy.pdf')
            
    except Exception as e:
        print(f'Error generating document: {e}')

# Send document to user
async def send_policy_document(update, user_data):
    await generate_policy_document(user_data)
    try:
        with open('additional/insurance_policy.pdf', 'rb') as pdf_file:
            await update.message.reply_document(document=pdf_file)  
        os.remove('additional/insurance_policy.pdf')
    except Exception as e:
        await update.message.reply_text(f'Error: {str(e)}')