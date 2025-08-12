"""
Конфигурация для Telegram-бота портных
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot настройки
BOT_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_ADMIN_ID = int(os.getenv('TELEGRAM_ADMIN_ID', 0))

# База данных
DATABASE_PATH = os.getenv('DATABASE_PATH', 'bot_data.db')

# Google Sheets настройки
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
WORKSHEET_NAME = os.getenv('WORKSHEET_NAME', 'Report')

# Настройки бота
MAX_PHOTOS = 3

# Проверка обязательных переменных
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

if not TELEGRAM_ADMIN_ID:
    raise ValueError("TELEGRAM_ADMIN_ID не найден в переменных окружения")

if not SPREADSHEET_ID:
    raise ValueError("SPREADSHEET_ID не найден в переменных окружения")