import os
from dotenv import load_dotenv
from openai import OpenAI
from mindee import Client

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
MINDEE_API_KEY = os.getenv('MINDEE_API_KEY')
PLATE_RECOGNIZER_TOKEN = os.getenv('PLATE_RECOGNIZER_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Ініціалізація клієнтів
openai_client = OpenAI(api_key=OPENAI_API_KEY)
mindee_client = Client(api_key=MINDEE_API_KEY)