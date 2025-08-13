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

# S3 Storage настройки
S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
S3_REGION = os.getenv('S3_REGION', 'us-east-1')

# Настройки бота
MAX_PHOTOS = 3

# Google Sheets структура
SHEETS_START_ROW = 1
SHEETS_COLUMNS = {
    'DATE': 'B',        # Дата
    'TIME': 'C',        # Время
    'CATEGORY': 'D',    # Категория
    'MASTER': 'E',      # Мастер
    'PHOTO_1': 'F',     # Фото 1
    'PHOTO_2': 'G',     # Фото 2
    'PHOTO_3': 'H',     # Фото 3
    'COMMENT': 'I'      # Комментарий
}

# Проверка обязательных переменных
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

if not TELEGRAM_ADMIN_ID:
    raise ValueError("TELEGRAM_ADMIN_ID не найден в переменных окружения")

if not SPREADSHEET_ID:
    raise ValueError("SPREADSHEET_ID не найден в переменных окружения")

# Проверка S3 переменных
if not all([S3_ENDPOINT_URL, S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_KEY]):
    raise ValueError("Не все S3 переменные настроены в .env файле")