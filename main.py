"""
Главный файл для запуска Telegram-бота портных
"""
import asyncio
import sys
import os

# Добавляем папки в путь
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'settings'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from bot.bot_manager import BotManager


async def main():
    """Основная функция запуска"""
    print("🚀 Запуск бота портных...")
    
    bot_manager = BotManager()
    await bot_manager.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)