"""
Модуль для работы с базой данных SQLite
"""
import sqlite3
import aiosqlite
import logging
from typing import List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, db_path: str = "bot_data.db"):
        self.db_path = db_path
    
    async def initialize(self):
        """Инициализация базы данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Таблица сотрудников
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS employees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_id INTEGER UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                """)
                
                # Таблица жалоб
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS complaints (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER,
                        category TEXT NOT NULL,
                        master_name TEXT NOT NULL,
                        comment TEXT NOT NULL,
                        photo_urls TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (employee_id) REFERENCES employees (id)
                    )
                """)
                
                await db.commit()
                logger.info("База данных успешно инициализирована")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    async def add_employee(self, telegram_id: int, name: str) -> bool:
        """
        Добавление нового сотрудника или реактивация существующего
        
        Args:
            telegram_id: Telegram ID сотрудника
            name: Имя и фамилия сотрудника
            
        Returns:
            bool: Успешность операции
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Проверяем, существует ли уже сотрудник (включая неактивных)
                cursor = await db.execute(
                    "SELECT id, is_active FROM employees WHERE telegram_id = ?",
                    (telegram_id,)
                )
                existing = await cursor.fetchone()
                
                if existing:
                    # Если сотрудник существует, но неактивен - реактивируем
                    if not existing[1]:  # is_active = 0
                        await db.execute(
                            "UPDATE employees SET name = ?, is_active = 1 WHERE telegram_id = ?",
                            (name, telegram_id)
                        )
                        await db.commit()
                        logger.info(f"Сотрудник реактивирован: {name} (ID: {telegram_id})")
                        return True
                    else:
                        logger.warning(f"Активный сотрудник с ID {telegram_id} уже существует")
                        return False
                else:
                    # Добавляем нового сотрудника
                    await db.execute(
                        "INSERT INTO employees (telegram_id, name) VALUES (?, ?)",
                        (telegram_id, name)
                    )
                    await db.commit()
                    logger.info(f"Сотрудник добавлен: {name} (ID: {telegram_id})")
                    return True
                
        except Exception as e:
            logger.error(f"Ошибка добавления сотрудника: {e}")
            return False
    
    async def get_employees(self) -> List[Tuple[int, int, str]]:
        """
        Получение списка всех активных сотрудников
        
        Returns:
            List[Tuple[int, int, str]]: Список (id, telegram_id, name)
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT id, telegram_id, name FROM employees WHERE is_active = 1 ORDER BY name"
                )
                employees = await cursor.fetchall()
                return employees
                
        except Exception as e:
            logger.error(f"Ошибка получения списка сотрудников: {e}")
            return []
    
    async def get_employee_by_telegram_id(self, telegram_id: int) -> Optional[Tuple[int, str]]:
        """
        Получение сотрудника по Telegram ID
        
        Args:
            telegram_id: Telegram ID сотрудника
            
        Returns:
            Optional[Tuple[int, str]]: (id, name) или None
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT id, name FROM employees WHERE telegram_id = ? AND is_active = 1",
                    (telegram_id,)
                )
                result = await cursor.fetchone()
                return result
                
        except Exception as e:
            logger.error(f"Ошибка поиска сотрудника: {e}")
            return None
    
    async def delete_employee(self, employee_id: int) -> bool:
        """
        Удаление сотрудника (деактивация)
        
        Args:
            employee_id: ID сотрудника в базе данных
            
        Returns:
            bool: Успешность операции
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "UPDATE employees SET is_active = 0 WHERE id = ?",
                    (employee_id,)
                )
                await db.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Сотрудник с ID {employee_id} деактивирован")
                    return True
                else:
                    logger.warning(f"Сотрудник с ID {employee_id} не найден")
                    return False
                    
        except Exception as e:
            logger.error(f"Ошибка удаления сотрудника: {e}")
            return False
    
    async def delete_employee_permanently(self, employee_id: int) -> bool:
        """
        Полное физическое удаление сотрудника из базы данных
        
        Args:
            employee_id: ID сотрудника в базе данных
            
        Returns:
            bool: Успешность операции
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Сначала удаляем связанные жалобы
                await db.execute(
                    "DELETE FROM complaints WHERE employee_id = ?",
                    (employee_id,)
                )
                
                # Затем удаляем самого сотрудника
                cursor = await db.execute(
                    "DELETE FROM employees WHERE id = ?",
                    (employee_id,)
                )
                await db.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Сотрудник с ID {employee_id} полностью удален")
                    return True
                else:
                    logger.warning(f"Сотрудник с ID {employee_id} не найден")
                    return False
                    
        except Exception as e:
            logger.error(f"Ошибка полного удаления сотрудника: {e}")
            return False
    
    async def is_employee_active(self, telegram_id: int) -> bool:
        """
        Проверка, является ли пользователь активным сотрудником
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            bool: True если активный сотрудник
        """
        employee = await self.get_employee_by_telegram_id(telegram_id)
        return employee is not None
    
    async def add_complaint(
        self, 
        employee_telegram_id: int,
        category: str,
        master_name: str,
        comment: str,
        photo_urls: List[str] = None
    ) -> bool:
        """
        Добавление жалобы в базу данных
        
        Args:
            employee_telegram_id: Telegram ID сотрудника
            category: Категория жалобы
            master_name: Имя мастера
            comment: Комментарий
            photo_urls: Список URL фотографий
            
        Returns:
            bool: Успешность операции
        """
        try:
            # Получаем ID сотрудника
            employee = await self.get_employee_by_telegram_id(employee_telegram_id)
            if not employee:
                logger.error(f"Сотрудник с Telegram ID {employee_telegram_id} не найден")
                return False
            
            employee_id = employee[0]
            
            # Преобразуем список URL в строку
            photo_urls_str = ",".join(photo_urls) if photo_urls else ""
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """INSERT INTO complaints 
                       (employee_id, category, master_name, comment, photo_urls) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (employee_id, category, master_name, comment, photo_urls_str)
                )
                await db.commit()
                
                logger.info(f"Жалоба добавлена от сотрудника {employee_telegram_id}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка добавления жалобы: {e}")
            return False
    
    async def get_complaints_count(self) -> int:
        """
        Получение общего количества жалоб
        
        Returns:
            int: Количество жалоб
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM complaints")
                result = await cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            logger.error(f"Ошибка получения количества жалоб: {e}")
            return 0