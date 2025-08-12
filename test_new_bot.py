"""
Тесты для новой структуры бота
"""
import asyncio
import sys
import os

# Добавляем папки в путь
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'settings'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from settings.config import BOT_TOKEN, TELEGRAM_ADMIN_ID
from settings.database import Database
from bot.enums import Categories, Messages, ButtonTexts
from bot.keyboards import Keyboards


async def test_config():
    """Тест конфигурации"""
    print("🔧 Тестирование конфигурации...")
    
    # Проверяем, что переменные определены (могут быть пустыми для теста)
    assert BOT_TOKEN is not None, "BOT_TOKEN не определен"
    assert TELEGRAM_ADMIN_ID is not None, "TELEGRAM_ADMIN_ID не определен"
    
    print("✅ Конфигурация загружена")


async def test_enums():
    """Тест перечислений"""
    print("📋 Тестирование перечислений...")
    
    # Проверяем категории
    categories = list(Categories)
    assert len(categories) == 4, f"Ожидалось 4 категории, получено {len(categories)}"
    
    # Проверяем сообщения
    assert Messages.WELCOME_ADMIN.value, "Приветствие админа не определено"
    assert Messages.WELCOME_EMPLOYEE.value, "Приветствие сотрудника не определено"
    
    # Проверяем тексты кнопок
    assert ButtonTexts.SEND_COMPLAINT.value, "Текст кнопки жалобы не определен"
    
    print("✅ Перечисления корректны")


async def test_keyboards():
    """Тест клавиатур"""
    print("⌨️ Тестирование клавиатур...")
    
    # Тестируем создание клавиатур
    admin_keyboard = Keyboards.main_menu_admin()
    employee_keyboard = Keyboards.main_menu_employee()
    categories_keyboard = Keyboards.categories()
    
    assert admin_keyboard.inline_keyboard, "Клавиатура админа пуста"
    assert employee_keyboard.inline_keyboard, "Клавиатура сотрудника пуста"
    assert categories_keyboard.inline_keyboard, "Клавиатура категорий пуста"
    
    # Проверяем количество кнопок
    assert len(admin_keyboard.inline_keyboard) == 2, "У админа должно быть 2 кнопки"
    assert len(employee_keyboard.inline_keyboard) == 1, "У сотрудника должна быть 1 кнопка"
    assert len(categories_keyboard.inline_keyboard) == 4, "Должно быть 4 категории"
    
    print("✅ Клавиатуры создаются корректно")


async def test_database():
    """Тест базы данных"""
    print("🗄️ Тестирование базы данных...")
    
    try:
        # Создаем тестовую базу данных
        db = Database("test_bot.db")
        await db.initialize()
        
        # Тестируем добавление сотрудника
        success = await db.add_employee(123456789, "Тестовый Сотрудник")
        assert success, "Не удалось добавить сотрудника"
        
        # Тестируем получение сотрудника
        employee = await db.get_employee_by_telegram_id(123456789)
        assert employee is not None, "Сотрудник не найден"
        assert employee[1] == "Тестовый Сотрудник", "Неверное имя сотрудника"
        
        # Тестируем список сотрудников
        employees = await db.get_employees()
        assert len(employees) >= 1, "Список сотрудников пуст"
        
        # Тестируем проверку активности
        is_active = await db.is_employee_active(123456789)
        assert is_active, "Сотрудник должен быть активным"
        
        print("✅ База данных работает корректно")
        
        # Удаляем тестовую базу
        import os
        if os.path.exists("test_bot.db"):
            os.remove("test_bot.db")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования базы данных: {e}")
        raise


async def test_imports():
    """Тест импортов"""
    print("📦 Тестирование импортов...")
    
    try:
        from bot.bot_manager import BotManager
        from bot.handlers import router
        from utils.media_handler import MediaHandler
        from utils.google_sheets import GoogleSheetsManager
        
        assert BotManager, "BotManager не импортирован"
        assert router, "Router не импортирован"
        assert MediaHandler, "MediaHandler не импортирован"
        assert GoogleSheetsManager, "GoogleSheetsManager не импортирован"
        
        print("✅ Все модули импортируются корректно")
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        raise


async def run_all_tests():
    """Запуск всех тестов"""
    print("🚀 Запуск тестов новой структуры бота...\n")
    
    tests = [
        test_config,
        test_enums,
        test_keyboards,
        test_database,
        test_imports
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"❌ Тест {test.__name__} провален: {e}")
            failed += 1
        print()
    
    print(f"📊 Результаты тестирования:")
    print(f"✅ Пройдено: {passed}")
    print(f"❌ Провалено: {failed}")
    print(f"📈 Общий результат: {passed}/{passed + failed}")
    
    if failed == 0:
        print("\n🎉 Все тесты пройдены успешно!")
        print("🚀 Бот готов к запуску!")
    else:
        print(f"\n⚠️ Есть проблемы, требующие внимания")


if __name__ == "__main__":
    asyncio.run(run_all_tests())