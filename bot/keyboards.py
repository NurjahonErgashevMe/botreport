"""
Клавиатуры для Telegram-бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Tuple

from .enums import CallbackData, ButtonTexts, Categories


class Keyboards:
    """Класс для создания клавиатур"""
    
    @staticmethod
    def main_menu_admin() -> InlineKeyboardMarkup:
        """Главное меню для администратора"""
        buttons = [
            [InlineKeyboardButton(
                text=ButtonTexts.SEND_COMPLAINT.value,
                callback_data=CallbackData.START_COMPLAINT.value
            )],
            [InlineKeyboardButton(
                text=ButtonTexts.MANAGE_EMPLOYEES.value,
                callback_data=CallbackData.EMPLOYEES_MENU.value
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def main_menu_employee() -> InlineKeyboardMarkup:
        """Главное меню для сотрудника"""
        buttons = [
            [InlineKeyboardButton(
                text=ButtonTexts.SEND_COMPLAINT.value,
                callback_data=CallbackData.START_COMPLAINT.value
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def employees_menu() -> InlineKeyboardMarkup:
        """Меню управления сотрудниками"""
        buttons = [
            [InlineKeyboardButton(
                text=ButtonTexts.ADD_EMPLOYEE.value,
                callback_data=CallbackData.ADD_EMPLOYEE.value
            )],
            [InlineKeyboardButton(
                text=ButtonTexts.LIST_EMPLOYEES.value,
                callback_data=CallbackData.LIST_EMPLOYEES.value
            )],
            [InlineKeyboardButton(
                text=ButtonTexts.DELETE_EMPLOYEE.value,
                callback_data=CallbackData.DELETE_EMPLOYEE.value
            )],
            [InlineKeyboardButton(
                text=ButtonTexts.BACK_TO_MAIN.value,
                callback_data=CallbackData.BACK_TO_MAIN.value
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def back_to_employees() -> InlineKeyboardMarkup:
        """Кнопка возврата к меню сотрудников"""
        buttons = [
            [InlineKeyboardButton(
                text=ButtonTexts.BACK_TO_EMPLOYEES.value,
                callback_data=CallbackData.BACK_TO_EMPLOYEES.value
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Кнопка возврата в главное меню"""
        buttons = [
            [InlineKeyboardButton(
                text=ButtonTexts.BACK_TO_MAIN.value,
                callback_data=CallbackData.BACK_TO_MAIN.value
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def categories() -> InlineKeyboardMarkup:
        """Клавиатура с категориями"""
        buttons = []
        for category in Categories:
            buttons.append([InlineKeyboardButton(
                text=category.value,
                callback_data=f"{CallbackData.CATEGORY_PREFIX.value}{category.value}"
            )])
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def masters(masters_list: List[Tuple[int, int, str]]) -> InlineKeyboardMarkup:
        """
        Клавиатура с мастерами
        
        Args:
            masters_list: Список кортежей (id, telegram_id, name)
        """
        buttons = []
        for _, _, name in masters_list:
            buttons.append([InlineKeyboardButton(
                text=name,
                callback_data=f"{CallbackData.MASTER_PREFIX.value}{name}"
            )])
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def photos() -> InlineKeyboardMarkup:
        """Клавиатура для работы с фото"""
        buttons = [
            [InlineKeyboardButton(
                text=ButtonTexts.ADD_PHOTO.value,
                callback_data=CallbackData.ADD_PHOTO.value
            )],
            [InlineKeyboardButton(
                text=ButtonTexts.SKIP_PHOTOS.value,
                callback_data=CallbackData.SKIP_PHOTOS.value
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def photos_next() -> InlineKeyboardMarkup:
        """Клавиатура для перехода к комментарию после фото"""
        buttons = [
            [InlineKeyboardButton(
                text=ButtonTexts.NEXT_TO_COMMENT.value,
                callback_data=CallbackData.SKIP_PHOTOS.value
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def preview() -> InlineKeyboardMarkup:
        """Клавиатура для предварительного просмотра"""
        buttons = [
            [InlineKeyboardButton(
                text=ButtonTexts.SAVE.value,
                callback_data=CallbackData.SAVE_COMPLAINT.value
            )],
            [InlineKeyboardButton(
                text=ButtonTexts.DELETE_AND_RESTART.value,
                callback_data=CallbackData.RESTART_COMPLAINT.value
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def send_another() -> InlineKeyboardMarkup:
        """Кнопка для отправки ещё одного замечания"""
        buttons = [
            [InlineKeyboardButton(
                text=ButtonTexts.SEND_ANOTHER.value,
                callback_data=CallbackData.START_COMPLAINT.value
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def delete_employees(employees: List[Tuple[int, int, str]]) -> InlineKeyboardMarkup:
        """
        Клавиатура для удаления сотрудников
        
        Args:
            employees: Список кортежей (id, telegram_id, name)
        """
        buttons = []
        
        # Добавляем кнопки с индексами сотрудников
        for i, (emp_id, _, _) in enumerate(employees, 1):
            buttons.append([InlineKeyboardButton(
                text=str(i),
                callback_data=f"delete_emp_{emp_id}"
            )])
        
        # Кнопка возврата
        buttons.append([InlineKeyboardButton(
            text=ButtonTexts.BACK_TO_EMPLOYEES.value,
            callback_data=CallbackData.BACK_TO_EMPLOYEES.value
        )])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def confirm_delete() -> InlineKeyboardMarkup:
        """Подтверждение удаления сотрудника"""
        buttons = [
            [InlineKeyboardButton(
                text=ButtonTexts.YES_DELETE.value,
                callback_data=CallbackData.CONFIRM_DELETE.value
            )],
            [InlineKeyboardButton(
                text=ButtonTexts.NO_CANCEL.value,
                callback_data=CallbackData.CANCEL_DELETE.value
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)