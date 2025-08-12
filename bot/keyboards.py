"""
Клавиатуры для Telegram-бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Tuple

from .enums import CallbackData, ButtonTexts, Categories


class Keyboards:
    """Класс для создания клавиатур"""
    
    @staticmethod
    def main_menu_admin() -> ReplyKeyboardMarkup:
        """Главное меню для администратора"""
        buttons = [
            [KeyboardButton(text=ButtonTexts.SEND_COMPLAINT.value)],
            [KeyboardButton(text=ButtonTexts.MANAGE_EMPLOYEES.value)]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    @staticmethod
    def main_menu_employee() -> ReplyKeyboardMarkup:
        """Главное меню для сотрудника"""
        buttons = [
            [KeyboardButton(text=ButtonTexts.SEND_COMPLAINT.value)]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    @staticmethod
    def employees_menu() -> ReplyKeyboardMarkup:
        """Меню управления сотрудниками"""
        buttons = [
            [KeyboardButton(text=ButtonTexts.ADD_EMPLOYEE.value)],
            [KeyboardButton(text=ButtonTexts.LIST_EMPLOYEES.value)],
            [KeyboardButton(text=ButtonTexts.DELETE_EMPLOYEE.value)],
            [KeyboardButton(text=ButtonTexts.BACK_TO_MAIN.value)]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    @staticmethod
    def back_to_employees() -> ReplyKeyboardMarkup:
        """Кнопка возврата к меню сотрудников"""
        buttons = [
            [KeyboardButton(text=ButtonTexts.BACK_TO_EMPLOYEES.value)]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    @staticmethod
    def back_to_main() -> ReplyKeyboardMarkup:
        """Кнопка возврата в главное меню"""
        buttons = [
            [KeyboardButton(text=ButtonTexts.BACK_TO_MAIN.value)]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    @staticmethod
    def categories() -> ReplyKeyboardMarkup:
        """Клавиатура с категориями"""
        buttons = []
        for category in Categories:
            buttons.append([KeyboardButton(text=category.value)])
        
        # Добавляем кнопку "Назад"
        buttons.append([KeyboardButton(text=ButtonTexts.BACK_TO_MAIN.value)])
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    

    
    @staticmethod
    def photos() -> ReplyKeyboardMarkup:
        """Клавиатура для работы с фото (когда фото еще нет)"""
        buttons = [
            [KeyboardButton(text=ButtonTexts.SKIP_PHOTOS.value)],
            [KeyboardButton(text=ButtonTexts.CANCEL_COMPLAINT.value)]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    @staticmethod
    def photos_with_finish() -> ReplyKeyboardMarkup:
        """Клавиатура для работы с фото (когда уже есть фото)"""
        buttons = [
            [KeyboardButton(text=ButtonTexts.FINISH_PHOTOS.value)],
            [KeyboardButton(text=ButtonTexts.CANCEL_COMPLAINT.value)]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    @staticmethod
    def photos_next() -> ReplyKeyboardMarkup:
        """Клавиатура для перехода к комментарию после фото"""
        buttons = [
            [KeyboardButton(text=ButtonTexts.NEXT_TO_COMMENT.value)],
            [KeyboardButton(text=ButtonTexts.CANCEL_COMPLAINT.value)]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    @staticmethod
    def preview() -> ReplyKeyboardMarkup:
        """Клавиатура для предварительного просмотра"""
        buttons = [
            [KeyboardButton(text=ButtonTexts.SAVE.value)],
            [KeyboardButton(text=ButtonTexts.DELETE_AND_RESTART.value)],
            [KeyboardButton(text=ButtonTexts.CANCEL_COMPLAINT.value)]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    @staticmethod
    def send_another() -> ReplyKeyboardMarkup:
        """Кнопка для отправки ещё одного замечания"""
        buttons = [
            [KeyboardButton(text=ButtonTexts.SEND_ANOTHER.value)],
            [KeyboardButton(text=ButtonTexts.BACK_TO_MAIN.value)]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    @staticmethod
    def comment_input() -> ReplyKeyboardMarkup:
        """Клавиатура для ввода комментария"""
        buttons = [
            [KeyboardButton(text=ButtonTexts.CANCEL_COMPLAINT.value)]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
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