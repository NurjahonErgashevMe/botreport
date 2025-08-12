"""
Состояния для FSM (Finite State Machine) бота
"""
from aiogram.fsm.state import State, StatesGroup


class ComplaintStates(StatesGroup):
    """Состояния для процесса подачи жалобы"""
    
    # Выбор категории
    choosing_category = State()
    
    # Выбор мастера
    choosing_master = State()
    
    # Загрузка фотографий
    uploading_photos = State()
    
    # Ввод комментария
    entering_comment = State()
    
    # Предварительный просмотр
    preview = State()


class EmployeeStates(StatesGroup):
    """Состояния для управления сотрудниками"""
    
    # Ввод ID сотрудника
    entering_employee_id = State()
    
    # Ввод имени сотрудника
    entering_employee_name = State()
    
    # Подтверждение удаления
    confirming_delete = State()