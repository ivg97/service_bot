import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')

# Временные интервалы для записи (в минутах)
TIME_SLOTS = [30, 60]
WORKING_HOURS = {'start': 9, 'end': 21}