"""
Модуль для работы с Google Sheets API
"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging
from typing import List, Optional

from settings.config import GOOGLE_CREDENTIALS_FILE, SPREADSHEET_ID, WORKSHEET_NAME

logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    """Менеджер для работы с Google Sheets"""
    
    def __init__(self):
        self.gc = None
        self.worksheet = None
        self.spreadsheet = None
    
    async def initialize(self):
        """Инициализация подключения к Google Sheets"""
        try:
            # Настройка авторизации
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                GOOGLE_CREDENTIALS_FILE, 
                scopes=scope
            )
            
            self.gc = gspread.authorize(creds)
            self.spreadsheet = self.gc.open_by_key(SPREADSHEET_ID)
            
            # Получаем или создаём рабочий лист
            try:
                self.worksheet = self.spreadsheet.worksheet(WORKSHEET_NAME)
            except gspread.WorksheetNotFound:
                self.worksheet = self.spreadsheet.add_worksheet(
                    title=WORKSHEET_NAME, 
                    rows=1000, 
                    cols=8
                )
                # Добавляем заголовки
                headers = [
                    'Дата', 'Время', 'Категория', 'Мастер', 
                    'Фото 1', 'Фото 2', 'Фото 3', 'Комментарий'
                ]
                self.worksheet.append_row(headers)
            
            logger.info("Google Sheets успешно инициализированы")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Google Sheets: {e}")
            raise
    
    async def add_complaint(
        self, 
        category: str, 
        master: str, 
        comment: str, 
        photo_urls: List[str] = None
    ) -> bool:
        """
        Добавление жалобы в таблицу
        
        Args:
            category: Категория жалобы
            master: Имя мастера
            comment: Комментарий
            photo_urls: Список URL фотографий
            
        Returns:
            bool: Успешность операции
        """
        try:
            now = datetime.now()
            date_str = now.strftime('%d.%m.%Y')
            time_str = now.strftime('%H:%M')
            
            # Подготовка данных для строки
            row_data = [date_str, time_str, category, master]
            
            # Добавление фотографий (до 3)
            photo_urls = photo_urls or []
            for i in range(3):
                if i < len(photo_urls):
                    # Пытаемся вставить как изображение
                    photo_cell = f'=IMAGE("{photo_urls[i]}")'
                    row_data.append(photo_cell)
                else:
                    row_data.append('')
            
            # Добавление комментария
            row_data.append(comment)
            
            # Добавление строки в таблицу
            self.worksheet.append_row(row_data)
            
            logger.info(f"Жалоба успешно добавлена: {category} - {master}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления жалобы: {e}")
            return False