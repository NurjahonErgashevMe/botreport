"""Модуль для работы с медиафайлами и S3 хранилищем"""
import logging
import asyncio
import uuid
import os
import tempfile
from datetime import datetime
from typing import Optional
from aiogram.types import PhotoSize, Voice
from aiogram import Bot
import boto3
from botocore.exceptions import ClientError
import aiohttp
import speech_recognition as sr
from pydub import AudioSegment

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
    
    async def get_photo_info(self, bot: Bot, message) -> Optional[dict]:
        try:
            # Если фото прислано как файл (документ) → без сжатия
            if message.document:
                file = await bot.get_file(message.document.file_id)
                width = None
                height = None
                file_size = message.document.file_size

            # Если как фото → берём последний элемент (самое большое доступное)
            elif message.photo:
                largest_photo = message.photo[-1]
                file = await bot.get_file(largest_photo.file_id)
                width = largest_photo.width
                height = largest_photo.height
                file_size = largest_photo.file_size

            else:
                logger.error("В сообщении нет фото или документа")
                return None

            telegram_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

            return {
                'file_id': file.file_id,
                'file_path': file.file_path,
                'telegram_url': telegram_url,
                'width': width,
                'height': height,
                'file_size': file_size
            }

        except Exception as e:
            logger.error(f"Ошибка получения информации о фото: {e}")
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
        """Распознавание голосового сообщения в текст"""
        ogg_path = None
        wav_path = None
        
        try:
            # Скачиваем голосовое сообщение
            file_info = await bot.get_file(voice.file_id)
            ogg_path = os.path.join(tempfile.gettempdir(), f"voice_{voice.file_id}.ogg")
            wav_path = os.path.join(tempfile.gettempdir(), f"voice_{voice.file_id}.wav")
            
            await bot.download_file(file_info.file_path, ogg_path)
            
            # Конвертируем в WAV в отдельном потоке
            await asyncio.get_event_loop().run_in_executor(
                None, self._convert_ogg_to_wav, ogg_path, wav_path
            )
            
            # Распознаем речь в отдельном потоке
            text = await asyncio.get_event_loop().run_in_executor(
                None, self._recognize_speech, wav_path
            )
            
            logger.info(f"Голосовое сообщение распознано: {len(text) if text else 0} символов")
            return text
            
        except Exception as e:
            logger.error(f"Ошибка обработки голосового сообщения: {e}")
            return None
        finally:
            # Очищаем временные файлы
            for file_path in [ogg_path, wav_path]:
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.warning(f"Не удалось удалить временный файл {file_path}: {e}")
    
    def _convert_ogg_to_wav(self, ogg_path: str, wav_path: str):
        """Конвертация OGG в WAV"""
        try:
            audio = AudioSegment.from_file(ogg_path)
            audio.export(wav_path, format="wav")
        except Exception as e:
            logger.error(f"Ошибка конвертации аудио: {e}")
            raise
    
    def _recognize_speech(self, wav_path: str) -> Optional[str]:
        """Распознавание речи из WAV файла"""
        try:
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(wav_path) as source:
                # Настройка для лучшего распознавания
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
            
            # Распознавание с помощью Google Speech API
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            return text
            
        except sr.UnknownValueError:
            logger.warning("Не удалось распознать речь в голосовом сообщении")
            return None
        except sr.RequestError as e:
            logger.error(f"Ошибка запроса к сервису распознавания: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка распознавания речи: {e}")
            return None