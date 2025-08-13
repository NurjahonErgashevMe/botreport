"""Модуль для работы с Google Sheets API"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
import logging
import asyncio
from typing import List, Optional

from settings.config import (
    GOOGLE_CREDENTIALS_FILE, SPREADSHEET_ID, WORKSHEET_NAME,
    SHEETS_START_ROW, SHEETS_COLUMNS
)

logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    def __init__(self):
        self.gc = None
        self.worksheet = None
        self.spreadsheet = None
    
    async def initialize(self):
        try:
            logger.info("Инициализация Google Sheets...")
            await asyncio.get_event_loop().run_in_executor(None, self._sync_initialize)
            logger.info("Google Sheets инициализированы")
        except Exception as e:
            logger.error(f"Ошибка инициализации Google Sheets: {e}")
            raise
    
    def _sync_initialize(self):
        try:
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=scope)
            self.gc = gspread.authorize(creds)
            self.spreadsheet = self.gc.open_by_key(SPREADSHEET_ID)
            
            try:
                self.worksheet = self.spreadsheet.worksheet(WORKSHEET_NAME)
            except gspread.WorksheetNotFound:
                self.worksheet = self.spreadsheet.add_worksheet(
                    title=WORKSHEET_NAME, 
                    rows=1000, 
                    cols=8
                )
                headers = ['Дата', 'Время', 'Категория', 'Мастер', 'Фото 1', 'Фото 2', 'Фото 3', 'Комментарий']
                self.worksheet.append_row(headers)
                
        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            raise
    
    async def add_complaint(self, category: str, master: str, comment: str, photo_urls: List[str] = None) -> bool:
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._sync_add_complaint, category, master, comment, photo_urls
            )
            return result
        except Exception as e:
            logger.error(f"Ошибка добавления жалобы: {e}")
            return False
    
    def _sync_add_complaint(self, category: str, master: str, comment: str, photo_urls: List[str] = None) -> bool:
        try:
            moscow_tz = pytz.timezone('Europe/Moscow')
            now = datetime.now(moscow_tz)
            date_str = now.strftime('%d.%m.%Y')
            time_str = now.strftime('%H:%M')
            
            # Находим следующую пустую строку
            all_values = self.worksheet.get_all_values()
            next_row = len(all_values) + 1
            
            data_to_update = {
                SHEETS_COLUMNS['DATE']: date_str,
                SHEETS_COLUMNS['TIME']: time_str,
                SHEETS_COLUMNS['CATEGORY']: category,
                SHEETS_COLUMNS['MASTER']: master,
                SHEETS_COLUMNS['COMMENT']: comment
            }
            
            photo_urls = photo_urls or []
            photo_columns = [SHEETS_COLUMNS['PHOTO_1'], SHEETS_COLUMNS['PHOTO_2'], SHEETS_COLUMNS['PHOTO_3']]
            
            for i, photo_url in enumerate(photo_urls[:3]):
                if photo_url:
                    data_to_update[photo_columns[i]] = f'=IMAGE("{photo_url}")'
                else:
                    data_to_update[photo_columns[i]] = ''
            
            for i in range(len(photo_urls), 3):
                data_to_update[photo_columns[i]] = ''
            
            updates = []
            for column, value in data_to_update.items():
                cell_address = f"{column}{next_row}"
                updates.append({
                    'range': cell_address,
                    'values': [[value]]
                })
            
            self.worksheet.batch_update(updates, value_input_option='USER_ENTERED')
            
            logger.info(f"Жалоба добавлена в строку {next_row}: {category} - {master}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления: {e}")
            return False