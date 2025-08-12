"""
Перечисления для бота
"""
from enum import Enum


class BotCommands(Enum):
    """Команды бота"""
    START = "/start"
    HELP = "/help"
    MENU = "/menu"


class CallbackData(Enum):
    """Callback данные для кнопок"""
    # Основное меню
    START_COMPLAINT = "start_complaint"
    EMPLOYEES_MENU = "employees_menu"
    BACK_TO_MAIN = "back_to_main"
    
    # Меню сотрудников
    ADD_EMPLOYEE = "add_employee"
    LIST_EMPLOYEES = "list_employees"
    DELETE_EMPLOYEE = "delete_employee"
    BACK_TO_EMPLOYEES = "back_to_employees"
    
    # Подтверждение удаления
    CONFIRM_DELETE = "confirm_delete"
    CANCEL_DELETE = "cancel_delete"
    
    # Процесс жалобы
    CATEGORY_PREFIX = "category_"
    MASTER_PREFIX = "master_"
    ADD_PHOTO = "add_photo"
    SKIP_PHOTOS = "skip_photos"
    SAVE_COMPLAINT = "save_complaint"
    RESTART_COMPLAINT = "restart"


class Categories(Enum):
    """Категории замечаний"""
    PATTERNS = "Лекала"
    TECH_CARDS = "Технические карты"
    MATERIALS = "Что-то заканчивается (материалы, фурнитура и т.п.)"
    OTHER = "Другое"


class Messages(Enum):
    """Текстовые сообщения"""
    # Приветствие
    WELCOME_ADMIN = (
        "👋 Добро пожаловать, администратор!\n\n"
        "Вы можете управлять системой приёма замечаний от портных.\n"
        "Выберите действие:"
    )
    
    WELCOME_EMPLOYEE = (
        "Здесь вы можете отправить замечание или предложение "
        "по работе с лекалами, техническими картами, материалами и другими вопросами.\n\n"
        "Нажмите кнопку ниже, чтобы начать:"
    )
    
    ACCESS_DENIED = (
        "❌ Доступ запрещён!\n\n"
        "У вас нет прав для использования этого бота."
    )
    
    # Сотрудники
    EMPLOYEES_MENU = (
        "👥 Управление сотрудниками\n\n"
        "Выберите действие:"
    )
    
    ADD_EMPLOYEE_ID = (
        "👤 Добавление нового сотрудника\n\n"
        "Введите Telegram ID сотрудника:"
    )
    
    ADD_EMPLOYEE_NAME = (
        "✅ ID принят!\n\n"
        "Теперь введите имя и фамилию сотрудника:"
    )
    
    EMPLOYEE_ADDED = (
        "✅ Сотрудник успешно добавлен!\n\n"
        "Теперь он может пользоваться ботом."
    )
    
    NO_EMPLOYEES = (
        "📝 Список сотрудников пуст\n\n"
        "Добавьте сотрудников для начала работы."
    )
    
    # Жалобы
    CHOOSE_CATEGORY = "📋 Выберите категорию замечания:"
    UPLOAD_PHOTOS = "📁 Загрузите фотографии (до 3) или пропустите этот шаг:"
    ENTER_COMMENT = (
        "💬 Введите комментарий к замечанию:\n\n"
        "Вы можете отправить текстовое сообщение или голосовое."
    )
    
    COMPLAINT_SAVED = (
        "✅ Замечание успешно сохранено!\n\n"
        "Спасибо за обратную связь. "
        "Ваше замечание будет рассмотрено."
    )
    
    COMPLAINT_ERROR = (
        "❌ Ошибка сохранения замечания.\n\n"
        "Попробуйте ещё раз или обратитесь к администратору."
    )


class ButtonTexts(Enum):
    """Тексты кнопок"""
    # Основное меню
    SEND_COMPLAINT = "📝 Отправить замечание"
    MANAGE_EMPLOYEES = "👥 Управление сотрудниками"
    
    # Меню сотрудников
    ADD_EMPLOYEE = "➕ Добавить сотрудника"
    LIST_EMPLOYEES = "📋 Список сотрудников"
    DELETE_EMPLOYEE = "🗑 Удалить сотрудника"
    BACK_TO_MAIN = "⬅️ Главное меню"
    BACK_TO_EMPLOYEES = "⬅️ Меню сотрудников"
    
    # Подтверждение
    YES_DELETE = "✅ Да, удалить"
    NO_CANCEL = "❌ Нет"
    
    # Фото
    ADD_PHOTO = "📷 Добавить фото"
    SKIP_PHOTOS = "➡️ Пропустить фото"
    NEXT_TO_COMMENT = "➡️ Перейти к комментарию"
    FINISH_PHOTOS = "✅ Загрузить и комментировать"
    
    # Предварительный просмотр
    SAVE = "✅ Сохранить"
    DELETE_AND_RESTART = "🗑 Удалить и начать заново"
    SEND_ANOTHER = "📝 Отправить ещё замечание"
    
    # Отмена
    CANCEL_COMPLAINT = "❌ Отменить"