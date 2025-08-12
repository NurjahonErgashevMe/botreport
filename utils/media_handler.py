"""Модуль для работы с медиафайлами и S3 хранилищем"""
import logging
import asyncio
import uuid
from datetime import datetime
from typing import Optional
from aiogram.types import PhotoSize, Voice
from aiogram import Bot
import boto3
from botocore.exceptions import ClientError
import aiohttp

from settings.config import (
    S3_ENDPOINT_URL, S3_BUCKET_NAME, S3_ACCESS_KEY, 
    S3_SECRET_KEY, S3_REGION
)

logger = logging.getLogger(__name__)


class MediaHandler:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION
        )
        logger.info("S3 клиент инициализирован")
    

    def _generate_unique_filename(self, employee_name: str, file_extension: str = "jpg") -> str:
        clean_name = "".join(c for c in employee_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '_')
        
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{clean_name}_{timestamp}_{unique_id}.{file_extension}"
    
    async def upload_photo_to_s3(self, bot: Bot, photo: PhotoSize, employee_name: str) -> Optional[str]:
        try:
            # Получаем файл из Telegram
            file = await bot.get_file(photo.file_id)
            telegram_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
            
            # Скачиваем файл
            async with aiohttp.ClientSession() as session:
                async with session.get(telegram_url) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка скачивания фото из Telegram: {response.status}")
                        return None
                    
                    photo_data = await response.read()
            
            # Генерируем уникальное имя файла
            filename = self._generate_unique_filename(employee_name)
            
            # Загружаем в S3
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self._sync_upload_to_s3, 
                photo_data, 
                filename
            )
            
            # Формируем публичную ссылку
            public_url = f"{S3_ENDPOINT_URL}/{S3_BUCKET_NAME}/{filename}"
            
            logger.info(f"Фото загружено в S3: {filename} ({photo.width}x{photo.height})")
            return public_url
            
        except Exception as e:
            logger.error(f"Ошибка загрузки фото в S3: {e}")
            return None
    
    def _sync_upload_to_s3(self, photo_data: bytes, filename: str):
        try:
            self.s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=filename,
                Body=photo_data,
                ContentType='image/jpeg',
                ACL='public-read'
            )
        except ClientError as e:
            logger.error(f"Ошибка загрузки в S3: {e}")
            raise
    
    async def get_photo_info(self, bot: Bot, photo: PhotoSize) -> Optional[dict]:
        try:
            file = await bot.get_file(photo.file_id)
            telegram_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
            
            photo_info = {
                'file_id': photo.file_id,
                'file_path': file.file_path,
                'telegram_url': telegram_url,
                'width': photo.width,
                'height': photo.height,
                'file_size': photo.file_size
            }
            
            logger.info(f"Получена информация о фото: {photo.file_id} ({photo.width}x{photo.height})")
            return photo_info
                
        except Exception as e:
            logger.error(f"Ошибка получения информации о фото: {e}")
            return None
    
    async def upload_photos_to_s3(self, bot: Bot, photo_infos: list, employee_name: str) -> list:
        s3_urls = []
        
        for photo_info in photo_infos:
            try:
                # Скачиваем фото из Telegram
                async with aiohttp.ClientSession() as session:
                    async with session.get(photo_info['telegram_url']) as response:
                        if response.status != 200:
                            logger.error(f"Ошибка скачивания фото: {response.status}")
                            continue
                        
                        photo_data = await response.read()
                
                # Генерируем уникальное имя файла
                filename = self._generate_unique_filename(employee_name)
                
                # Загружаем в S3
                await asyncio.get_event_loop().run_in_executor(
                    None, 
                    self._sync_upload_to_s3, 
                    photo_data, 
                    filename
                )
                
                # Формируем публичную ссылку
                public_url = f"{S3_ENDPOINT_URL}/{S3_BUCKET_NAME}/{filename}"
                s3_urls.append(public_url)
                
                logger.info(f"Фото загружено в S3: {filename}")
                
            except Exception as e:
                logger.error(f"Ошибка загрузки фото в S3: {e}")
                continue
        
        return s3_urls
    
    async def process_voice_message(self, bot: Bot, voice: Voice) -> Optional[str]:
        try:
            return "[Голосовое сообщение - функция распознавания в разработке]"
        except Exception as e:
            logger.error(f"Ошибка обработки голосового сообщения: {e}")
            return None