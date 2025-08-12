"""
Обработчики сообщений для Telegram-бота
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
import logging

from settings.config import TELEGRAM_ADMIN_ID
from settings.database import Database
from utils.google_sheets import GoogleSheetsManager
from .states import ComplaintStates, EmployeeStates
from .keyboards import Keyboards
from .enums import CallbackData, Messages, Categories
from utils.media_handler import MediaHandler

logger = logging.getLogger(__name__)
router = Router()

# Инициализация компонентов
db = Database()
media_handler = MediaHandler()
sheets_manager = GoogleSheetsManager()


async def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id == TELEGRAM_ADMIN_ID


async def has_access(user_id: int) -> bool:
    """Проверка доступа пользователя к боту"""
    if await is_admin(user_id):
        return True
    return await db.is_employee_active(user_id)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Проверяем, что это приватный чат
    if message.chat.type != "private":
        await message.answer("❌ Бот работает только в приватных чатах.")
        return
    
    user_id = message.from_user.id
    
    # Проверяем доступ
    if not await has_access(user_id):
        await message.answer(Messages.ACCESS_DENIED.value)
        return
    
    await state.clear()
    
    # Определяем тип пользователя и показываем соответствующее меню
    if await is_admin(user_id):
        keyboard = Keyboards.main_menu_admin()
        text = Messages.WELCOME_ADMIN.value
    else:
        keyboard = Keyboards.main_menu_employee()
        text = Messages.WELCOME_EMPLOYEE.value
    
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == CallbackData.BACK_TO_MAIN.value)
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await callback.answer()
    await state.clear()
    
    user_id = callback.from_user.id
    
    if await is_admin(user_id):
        keyboard = Keyboards.main_menu_admin()
        text = Messages.WELCOME_ADMIN.value
    else:
        keyboard = Keyboards.main_menu_employee()
        text = Messages.WELCOME_EMPLOYEE.value
    
    await callback.message.edit_text(text, reply_markup=keyboard)


# === УПРАВЛЕНИЕ СОТРУДНИКАМИ ===

@router.callback_query(F.data == CallbackData.EMPLOYEES_MENU.value)
async def employees_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления сотрудниками"""
    await callback.answer()
    
    # Проверяем права администратора
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Недостаточно прав", show_alert=True)
        return
    
    await state.clear()
    keyboard = Keyboards.employees_menu()
    await callback.message.edit_text(Messages.EMPLOYEES_MENU.value, reply_markup=keyboard)


@router.callback_query(F.data == CallbackData.BACK_TO_EMPLOYEES.value)
async def back_to_employees(callback: CallbackQuery, state: FSMContext):
    """Возврат в меню сотрудников"""
    await callback.answer()
    await state.clear()
    
    keyboard = Keyboards.employees_menu()
    await callback.message.edit_text(Messages.EMPLOYEES_MENU.value, reply_markup=keyboard)


@router.callback_query(F.data == CallbackData.ADD_EMPLOYEE.value)
async def add_employee_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления сотрудника"""
    await callback.answer()
    
    await state.set_state(EmployeeStates.entering_employee_id)
    await callback.message.edit_text(Messages.ADD_EMPLOYEE_ID.value)


@router.message(StateFilter(EmployeeStates.entering_employee_id))
async def add_employee_id(message: Message, state: FSMContext):
    """Ввод ID сотрудника"""
    try:
        employee_id = int(message.text.strip())
        
        # Проверяем, не существует ли уже такой сотрудник
        existing = await db.get_employee_by_telegram_id(employee_id)
        if existing:
            await message.answer("❌ Сотрудник с таким ID уже существует!")
            return
        
        await state.update_data(employee_id=employee_id)
        await state.set_state(EmployeeStates.entering_employee_name)
        await message.answer(Messages.ADD_EMPLOYEE_NAME.value)
        
    except ValueError:
        await message.answer("❌ Неверный формат ID. Введите числовой ID:")


@router.message(StateFilter(EmployeeStates.entering_employee_name))
async def add_employee_name(message: Message, state: FSMContext):
    """Ввод имени сотрудника"""
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer("❌ Имя слишком короткое. Введите полное имя:")
        return
    
    data = await state.get_data()
    employee_id = data['employee_id']
    
    # Добавляем сотрудника в базу данных
    success = await db.add_employee(employee_id, name)
    
    if success:
        await message.answer(Messages.EMPLOYEE_ADDED.value, reply_markup=Keyboards.back_to_employees())
        logger.info(f"Добавлен сотрудник: {name} (ID: {employee_id})")
    else:
        await message.answer("❌ Ошибка добавления сотрудника", reply_markup=Keyboards.back_to_employees())
    
    await state.clear()


@router.callback_query(F.data == CallbackData.LIST_EMPLOYEES.value)
async def list_employees(callback: CallbackQuery):
    """Показ списка сотрудников"""
    await callback.answer()
    
    employees = await db.get_employees()
    
    if not employees:
        await callback.message.edit_text(
            Messages.NO_EMPLOYEES.value,
            reply_markup=Keyboards.back_to_employees()
        )
        return
    
    # Формируем список сотрудников
    text = "👥 Список сотрудников:\n\n"
    for _, telegram_id, name in employees:
        text += f"• {name} - _{telegram_id}_\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=Keyboards.back_to_employees(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == CallbackData.DELETE_EMPLOYEE.value)
async def delete_employee_start(callback: CallbackQuery):
    """Начало удаления сотрудника"""
    await callback.answer()
    
    employees = await db.get_employees()
    
    if not employees:
        await callback.message.edit_text(
            Messages.NO_EMPLOYEES.value,
            reply_markup=Keyboards.back_to_employees()
        )
        return
    
    # Формируем список для удаления
    text = "🗑 Выберите сотрудника для удаления:\n\n"
    for i, (_, _, name) in enumerate(employees, 1):
        text += f"{i}. {name}\n"
    
    keyboard = Keyboards.delete_employees(employees)
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("delete_emp_"))
async def confirm_delete_employee(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления сотрудника"""
    await callback.answer()
    
    employee_id = int(callback.data.replace("delete_emp_", ""))
    
    # Получаем информацию о сотруднике
    employees = await db.get_employees()
    employee_info = None
    
    for emp_id, telegram_id, name in employees:
        if emp_id == employee_id:
            employee_info = (emp_id, telegram_id, name)
            break
    
    if not employee_info:
        await callback.message.edit_text(
            "❌ Сотрудник не найден",
            reply_markup=Keyboards.back_to_employees()
        )
        return
    
    # Сохраняем ID для подтверждения
    await state.update_data(delete_employee_id=employee_id)
    
    text = f"❓ Точно ли вы хотите удалить сотрудника {employee_info[2]}?"
    keyboard = Keyboards.confirm_delete()
    
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == CallbackData.CONFIRM_DELETE.value)
async def delete_employee_confirmed(callback: CallbackQuery, state: FSMContext):
    """Подтвержденное удаление сотрудника"""
    await callback.answer()
    
    data = await state.get_data()
    employee_id = data.get('delete_employee_id')
    
    if not employee_id:
        await callback.message.edit_text(
            "❌ Ошибка удаления",
            reply_markup=Keyboards.back_to_employees()
        )
        return
    
    success = await db.delete_employee(employee_id)
    
    if success:
        text = "✅ Сотрудник успешно удален!"
    else:
        text = "❌ Ошибка удаления сотрудника"
    
    await callback.message.edit_text(text, reply_markup=Keyboards.back_to_employees())
    await state.clear()


@router.callback_query(F.data == CallbackData.CANCEL_DELETE.value)
async def cancel_delete_employee(callback: CallbackQuery, state: FSMContext):
    """Отмена удаления сотрудника"""
    await callback.answer()
    await state.clear()
    
    keyboard = Keyboards.employees_menu()
    await callback.message.edit_text(Messages.EMPLOYEES_MENU.value, reply_markup=keyboard)


# === ПРОЦЕСС ПОДАЧИ ЖАЛОБЫ ===

@router.callback_query(F.data == CallbackData.START_COMPLAINT.value)
async def start_complaint(callback: CallbackQuery, state: FSMContext):
    """Начало процесса подачи жалобы"""
    await callback.answer()
    
    # Проверяем доступ
    if not await has_access(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    await state.set_state(ComplaintStates.choosing_category)
    
    keyboard = Keyboards.categories()
    await callback.message.edit_text(Messages.CHOOSE_CATEGORY.value, reply_markup=keyboard)


@router.callback_query(F.data.startswith(CallbackData.CATEGORY_PREFIX.value), StateFilter(ComplaintStates.choosing_category))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    """Выбор категории"""
    await callback.answer()
    
    category = callback.data.replace(CallbackData.CATEGORY_PREFIX.value, "")
    await state.update_data(category=category)
    
    # Получаем список мастеров (сотрудников)
    employees = await db.get_employees()
    
    if not employees:
        await callback.message.edit_text(
            "❌ Список мастеров пуст. Обратитесь к администратору.",
            reply_markup=Keyboards.back_to_main()
        )
        return
    
    await state.set_state(ComplaintStates.choosing_master)
    
    text = f"✅ Категория: {category}\n\n{Messages.CHOOSE_MASTER.value}"
    keyboard = Keyboards.masters(employees)
    
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith(CallbackData.MASTER_PREFIX.value), StateFilter(ComplaintStates.choosing_master))
async def choose_master(callback: CallbackQuery, state: FSMContext):
    """Выбор мастера"""
    await callback.answer()
    
    master = callback.data.replace(CallbackData.MASTER_PREFIX.value, "")
    await state.update_data(master=master)
    
    data = await state.get_data()
    
    await state.set_state(ComplaintStates.uploading_photos)
    await state.update_data(photos=[])
    
    text = (
        f"✅ Категория: {data['category']}\n"
        f"✅ Мастер: {master}\n\n"
        f"{Messages.UPLOAD_PHOTOS.value}"
    )
    
    keyboard = Keyboards.photos()
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == CallbackData.ADD_PHOTO.value, StateFilter(ComplaintStates.uploading_photos))
async def add_photo_prompt(callback: CallbackQuery, state: FSMContext):
    """Запрос на добавление фото"""
    await callback.answer()
    
    data = await state.get_data()
    photos_count = len(data.get('photos', []))
    
    if photos_count >= 3:  # MAX_PHOTOS
        await callback.answer("❌ Максимум 3 фотографии", show_alert=True)
        return
    
    text = f"📷 Отправьте фотографию ({photos_count + 1}/3)"
    await callback.message.edit_text(text)


@router.message(F.photo, StateFilter(ComplaintStates.uploading_photos))
async def handle_photo(message: Message, state: FSMContext):
    """Обработка загруженного фото"""
    data = await state.get_data()
    photos = data.get('photos', [])
    
    if len(photos) >= 3:  # MAX_PHOTOS
        await message.answer("❌ Максимум 3 фотографии")
        return
    
    # Получаем URL фотографии
    photo_url = await media_handler.get_photo_url(message.bot, message.photo[-1])
    
    if photo_url:
        photos.append(photo_url)
        await state.update_data(photos=photos)
        
        text = f"✅ Фото {len(photos)}/3 загружено\n\nЗагрузите ещё фото или перейдите к комментарию:"
        
        if len(photos) >= 3:
            keyboard = Keyboards.photos_next()
        else:
            keyboard = Keyboards.photos()
        
        await message.answer(text, reply_markup=keyboard)
    else:
        await message.answer("❌ Ошибка загрузки фото. Попробуйте ещё раз.")


@router.callback_query(F.data == CallbackData.SKIP_PHOTOS.value, StateFilter(ComplaintStates.uploading_photos))
async def skip_photos(callback: CallbackQuery, state: FSMContext):
    """Пропуск загрузки фото"""
    await callback.answer()
    
    await state.set_state(ComplaintStates.entering_comment)
    await callback.message.edit_text(Messages.ENTER_COMMENT.value)


@router.message(F.text, StateFilter(ComplaintStates.entering_comment))
async def handle_text_comment(message: Message, state: FSMContext):
    """Обработка текстового комментария"""
    await state.update_data(comment=message.text)
    await show_preview(message, state)


@router.message(F.voice, StateFilter(ComplaintStates.entering_comment))
async def handle_voice_comment(message: Message, state: FSMContext):
    """Обработка голосового комментария"""
    comment = await media_handler.process_voice_message(message.bot, message.voice)
    
    if comment:
        await state.update_data(comment=comment)
        await show_preview(message, state)
    else:
        await message.answer("❌ Ошибка обработки голосового сообщения. Попробуйте отправить текст.")


async def show_preview(message: Message, state: FSMContext):
    """Показ предварительного просмотра"""
    data = await state.get_data()
    
    await state.set_state(ComplaintStates.preview)
    
    photos_text = ""
    if data.get('photos'):
        photos_text = f"\n📷 Фотографий: {len(data['photos'])}"
    
    preview_text = (
        "📋 Предварительный просмотр замечания:\n\n"
        f"📂 Категория: {data['category']}\n"
        f"👤 Мастер: {data['master']}\n"
        f"💬 Комментарий: {data['comment']}"
        f"{photos_text}\n\n"
        "Сохранить замечание?"
    )
    
    keyboard = Keyboards.preview()
    await message.answer(preview_text, reply_markup=keyboard)


@router.callback_query(F.data == CallbackData.SAVE_COMPLAINT.value, StateFilter(ComplaintStates.preview))
async def save_complaint(callback: CallbackQuery, state: FSMContext):
    """Сохранение жалобы"""
    await callback.answer()
    
    data = await state.get_data()
    
    # Сохраняем в базу данных
    db_success = await db.add_complaint(
        employee_telegram_id=callback.from_user.id,
        category=data['category'],
        master_name=data['master'],
        comment=data['comment'],
        photo_urls=data.get('photos', [])
    )
    
    # Сохраняем в Google Sheets
    sheets_success = await sheets_manager.add_complaint(
        category=data['category'],
        master=data['master'],
        comment=data['comment'],
        photo_urls=data.get('photos', [])
    )
    
    if db_success and sheets_success:
        text = Messages.COMPLAINT_SAVED.value
    elif db_success:
        text = "✅ Замечание сохранено в базу данных!\n⚠️ Ошибка отправки в Google Sheets."
    else:
        text = Messages.COMPLAINT_ERROR.value
    
    keyboard = Keyboards.send_another()
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.clear()


@router.callback_query(F.data == CallbackData.RESTART_COMPLAINT.value)
async def restart_complaint(callback: CallbackQuery, state: FSMContext):
    """Перезапуск процесса подачи жалобы"""
    await callback.answer()
    await state.clear()
    await start_complaint(callback, state)


@router.message()
async def handle_other_messages(message: Message):
    """Обработчик прочих сообщений"""
    if message.chat.type != "private":
        return
    
    # Проверяем доступ
    if not await has_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED.value)
        return
    
    text = "❓ Не понимаю команду.\n\nИспользуйте /start для начала работы с ботом."
    await message.answer(text)