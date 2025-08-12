"""
Модуль для работы с медиафайлами
"""
import logging
from typing import Optional
from aiogram.types import PhotoSize, Voice
from aiogram import Bot

logger = logging.getLogger(__name__)


class MediaHandler:
    """Обработчик медиафайлов"""
    
    async def get_photo_url(self, bot: Bot, photo: PhotoSize) -> Optional[str]:
        """
        Получение URL фотографии
        
        Args:
            bot: Экземпляр бота
            photo: Объект фотографии
            
        Returns:
            str: URL фотографии или None
        """
        try:
            # Получаем файл
            file = await bot.get_file(photo.file_id)
            file_path = file.file_path
            
            # Возвращаем прямую ссылку Telegram
            return f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
                
        except Exception as e:
            logger.error(f"Ошибка получения URL фото: {e}")
            return None
    
    async def process_voice_message(self, bot: Bot, voice: Voice) -> Optional[str]:
        """
        Обработка голосового сообщения
        
        Args:
            bot: Экземпляр бота
            voice: Объект голосового сообщения
            
        Returns:
            str: Заглушка для голосового сообщения
        """
        try:
            # Пока возвращаем заглушку
            # В будущем можно интегрировать распознавание речи
            return "[Голосовое сообщение - функция распознавания в разработке]"
            
        except Exception as e:
            logger.error(f"Ошибка обработки голосового сообщения: {e}")
            return None