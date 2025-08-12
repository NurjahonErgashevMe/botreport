"""
Менеджер Telegram-бота для приёма жалоб портных
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from settings.config import BOT_TOKEN
from settings.database import Database
from utils.google_sheets import GoogleSheetsManager
from .handlers import router, sheets_manager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BotManager:
    """Менеджер бота"""
    
    def __init__(self):
        self.bot = None
        self.dp = None
        self.db = None
    
    async def initialize(self):
        """Инициализация компонентов бота"""
        try:
            # Инициализация бота и диспетчера
            self.bot = Bot(token=BOT_TOKEN)
            storage = MemoryStorage()
            self.dp = Dispatcher(storage=storage)
            
            # Подключение роутеров
            self.dp.include_router(router)
            
            # Инициализация базы данных
            self.db = Database()
            await self.db.initialize()
            
            # Инициализация Google Sheets
            await sheets_manager.initialize()
            
            logger.info("Все компоненты бота успешно инициализированы")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации бота: {e}")
            raise
    
    async def start(self):
        """Запуск бота"""
        try:
            await self.initialize()
            
            logger.info("🚀 Бот запущен и готов к работе")
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"Ошибка при работе бота: {e}")
            raise
        finally:
            if self.bot:
                await self.bot.session.close()
    
    async def stop(self):
        """Остановка бота"""
        if self.bot:
            await self.bot.session.close()
        logger.info("⏹️ Бот остановлен")