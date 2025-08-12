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
from .enums import CallbackData, Messages, Categories, ButtonTexts
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
        # Получаем имя сотрудника для персонализированного приветствия
        employee = await db.get_employee_by_telegram_id(user_id)
        if employee:
            employee_name = employee[1]  # employee[1] содержит имя сотрудника
            text = f"👋 Здравствуйте, {employee_name}!\n\n{Messages.WELCOME_EMPLOYEE.value}"
        else:
            text = Messages.WELCOME_EMPLOYEE.value
        
        keyboard = Keyboards.main_menu_employee()
    
    await message.answer(text, reply_markup=keyboard)


# === ОБРАБОТЧИКИ КНОПОК ГЛАВНОГО МЕНЮ ===

@router.message(F.text == ButtonTexts.BACK_TO_MAIN.value)
async def back_to_main(message: Message, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    
    user_id = message.from_user.id
    
    if await is_admin(user_id):
        keyboard = Keyboards.main_menu_admin()
        text = Messages.WELCOME_ADMIN.value
    else:
        # Получаем имя сотрудника для персонализированного приветствия
        employee = await db.get_employee_by_telegram_id(user_id)
        if employee:
            employee_name = employee[1]  # employee[1] содержит имя сотрудника
            text = f"👋 Здравствуйте, {employee_name}!\n\n{Messages.WELCOME_EMPLOYEE.value}"
        else:
            text = Messages.WELCOME_EMPLOYEE.value
        
        keyboard = Keyboards.main_menu_employee()
    
    await message.answer(text, reply_markup=keyboard)

@router.message(F.text == ButtonTexts.SEND_COMPLAINT.value)
async def start_complaint_handler(message: Message, state: FSMContext):
    """Обработчик кнопки отправки замечания"""
    # Проверяем доступ
    if not await has_access(message.from_user.id):
        await message.answer("❌ Доступ запрещён")
        return
    
    await start_complaint_process(message, state)

@router.message(F.text == ButtonTexts.MANAGE_EMPLOYEES.value)
async def employees_menu_handler(message: Message, state: FSMContext):
    """Обработчик кнопки управления сотрудниками"""
    # Проверяем права администратора
    if not await is_admin(message.from_user.id):
        await message.answer("❌ Недостаточно прав")
        return
    
    await state.clear()
    keyboard = Keyboards.employees_menu()
    await message.answer(Messages.EMPLOYEES_MENU.value, reply_markup=keyboard)


# === УПРАВЛЕНИЕ СОТРУДНИКАМИ ===

@router.message(F.text == ButtonTexts.BACK_TO_EMPLOYEES.value)
async def back_to_employees(message: Message, state: FSMContext):
    """Возврат в меню сотрудников"""
    await state.clear()
    
    keyboard = Keyboards.employees_menu()
    await message.answer(Messages.EMPLOYEES_MENU.value, reply_markup=keyboard)

@router.message(F.text == ButtonTexts.ADD_EMPLOYEE.value)
async def add_employee_start(message: Message, state: FSMContext):
    """Начало добавления сотрудника"""
    await state.set_state(EmployeeStates.entering_employee_id)
    await message.answer(Messages.ADD_EMPLOYEE_ID.value, reply_markup=Keyboards.back_to_employees())


@router.message(StateFilter(EmployeeStates.entering_employee_id))
async def add_employee_id(message: Message, state: FSMContext):
    """Ввод ID сотрудника"""
    # Проверяем на кнопку "Назад"
    if message.text == ButtonTexts.BACK_TO_EMPLOYEES.value:
        await back_to_employees(message, state)
        return
    
    try:
        employee_id = int(message.text.strip())
        
        # Проверяем, не существует ли уже активный сотрудник с таким ID
        existing = await db.get_employee_by_telegram_id(employee_id)
        if existing:
            await message.answer("❌ Активный сотрудник с таким ID уже существует!")
            return
        
        await state.update_data(employee_id=employee_id)
        await state.set_state(EmployeeStates.entering_employee_name)
        await message.answer(Messages.ADD_EMPLOYEE_NAME.value)
        
    except ValueError:
        await message.answer("❌ Неверный формат ID. Введите числовой ID:")


@router.message(StateFilter(EmployeeStates.entering_employee_name))
async def add_employee_name(message: Message, state: FSMContext):
    """Ввод имени сотрудника"""
    # Проверяем на кнопку "Назад"
    if message.text == ButtonTexts.BACK_TO_EMPLOYEES.value:
        await back_to_employees(message, state)
        return
    
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer("❌ Имя слишком короткое. Введите полное имя:")
        return
    
    data = await state.get_data()
    employee_id = data['employee_id']
    
    # Добавляем сотрудника в базу данных
    success = await db.add_employee(employee_id, name)
    
    if success:
        await message.answer(Messages.EMPLOYEE_ADDED.value, reply_markup=Keyboards.employees_menu())
        logger.info(f"Сотрудник обработан: {name} (ID: {employee_id})")
    else:
        await message.answer("❌ Ошибка добавления сотрудника", reply_markup=Keyboards.employees_menu())
    
    await state.clear()


@router.message(F.text == ButtonTexts.LIST_EMPLOYEES.value)
async def list_employees(message: Message):
    """Показ списка сотрудников"""
    employees = await db.get_employees()
    
    if not employees:
        await message.answer(
            Messages.NO_EMPLOYEES.value,
            reply_markup=Keyboards.employees_menu()
        )
        return
    
    # Формируем список сотрудников
    text = "👥 Список сотрудников:\n\n"
    for _, telegram_id, name in employees:
        text += f"• {name} - _{telegram_id}_\n"
    
    await message.answer(
        text,
        reply_markup=Keyboards.employees_menu(),
        parse_mode="Markdown"
    )


@router.message(F.text == ButtonTexts.DELETE_EMPLOYEE.value)
async def delete_employee_start(message: Message):
    """Начало удаления сотрудника"""
    employees = await db.get_employees()
    
    if not employees:
        await message.answer(
            Messages.NO_EMPLOYEES.value,
            reply_markup=Keyboards.employees_menu()
        )
        return
    
    # Формируем список для удаления
    text = "🗑 Выберите сотрудника для удаления:\n\n"
    for i, (_, _, name) in enumerate(employees, 1):
        text += f"{i}. {name}\n"
    
    keyboard = Keyboards.delete_employees(employees)
    await message.answer(text, reply_markup=keyboard)


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
        await callback.message.edit_text("❌ Сотрудник не найден")
        await callback.message.answer("Возвращаемся в меню сотрудников", reply_markup=Keyboards.employees_menu())
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
        await callback.message.edit_text("❌ Ошибка удаления")
        await callback.message.answer("Возвращаемся в меню сотрудников", reply_markup=Keyboards.employees_menu())
        return
    
    success = await db.delete_employee(employee_id)
    
    if success:
        text = "✅ Сотрудник успешно удален!"
    else:
        text = "❌ Ошибка удаления сотрудника"
    
    await callback.message.edit_text(text)
    await callback.message.answer("Возвращаемся в меню сотрудников", reply_markup=Keyboards.employees_menu())
    await state.clear()


@router.callback_query(F.data == CallbackData.CANCEL_DELETE.value)
async def cancel_delete_employee(callback: CallbackQuery, state: FSMContext):
    """Отмена удаления сотрудника"""
    await callback.answer()
    await state.clear()
    
    await callback.message.edit_text("Удаление отменено")
    await callback.message.answer(Messages.EMPLOYEES_MENU.value, reply_markup=Keyboards.employees_menu())


# === ПРОЦЕСС ПОДАЧИ ЖАЛОБЫ ===

async def start_complaint_process(message: Message, state: FSMContext):
    """Начало процесса подачи жалобы"""
    await state.set_state(ComplaintStates.choosing_category)
    
    keyboard = Keyboards.categories()
    await message.answer(Messages.CHOOSE_CATEGORY.value, reply_markup=keyboard)


@router.message(StateFilter(ComplaintStates.choosing_category))
async def choose_category(message: Message, state: FSMContext):
    """Выбор категории"""
    # Проверяем на кнопку "Назад"
    if message.text == ButtonTexts.BACK_TO_MAIN.value:
        await back_to_main(message, state)
        return
    
    # Проверяем, что выбрана валидная категория
    valid_categories = [cat.value for cat in Categories]
    if message.text not in valid_categories:
        await message.answer("❌ Пожалуйста, выберите категорию из предложенных вариантов:")
        return
    
    category = message.text
    await state.update_data(category=category)
    
    # Автоматически определяем мастера по Telegram ID отправителя
    employee = await db.get_employee_by_telegram_id(message.from_user.id)
    
    if not employee:
        await message.answer(
            "❌ Ошибка: вы не найдены в списке сотрудников. Обратитесь к администратору.",
            reply_markup=Keyboards.back_to_main()
        )
        return
    
    master_name = employee[1]  # employee[1] содержит имя сотрудника
    await state.update_data(master=master_name)
    
    await state.set_state(ComplaintStates.uploading_photos)
    await state.update_data(photos=[])
    
    text = (
        f"✅ Категория: {category}\n"
        f"✅ Мастер: {master_name}\n\n"
        f"{Messages.UPLOAD_PHOTOS.value}"
    )
    
    keyboard = Keyboards.photos()
    await message.answer(text, reply_markup=keyboard)





@router.message(F.text == ButtonTexts.SKIP_PHOTOS.value, StateFilter(ComplaintStates.uploading_photos))
async def skip_photos(message: Message, state: FSMContext):
    """Пропуск загрузки фото"""
    await state.set_state(ComplaintStates.entering_comment)
    await message.answer(Messages.ENTER_COMMENT.value, reply_markup=Keyboards.comment_input())

@router.message(F.text == ButtonTexts.CANCEL_COMPLAINT.value)
async def cancel_complaint(message: Message, state: FSMContext):
    """Отмена подачи жалобы"""
    await back_to_main(message, state)


@router.message(F.photo, StateFilter(ComplaintStates.uploading_photos))
async def handle_photo(message: Message, state: FSMContext):
    """Обработка загруженного фото"""
    data = await state.get_data()
    photos = data.get('photos', [])
    
    if len(photos) >= 3:  # MAX_PHOTOS
        await message.answer("❌ Максимум 3 фотографии")
        return
    
    # Получаем информацию о фотографии (без загрузки в S3)
    photo_info = await media_handler.get_photo_info(message.bot, message.photo[-1])
    
    if photo_info:
        # Сохраняем информацию о фото для последующей загрузки в S3
        photos.append(photo_info)
        await state.update_data(photos=photos)
        
        if len(photos) >= 3:
            # Если загружено 3 фото - автоматически переходим к комментарию
            text = f"✅ Фото {len(photos)}/3 загружено\n\nВсе фотографии загружены. Теперь добавьте комментарий:"
            keyboard = Keyboards.photos_next()
        else:
            # Если меньше 3 фото - предлагаем загрузить еще или завершить
            text = f"✅ Фото {len(photos)}/3 загружено\n\nЗагрузите ещё фото или перейдите к комментарию:"
            keyboard = Keyboards.photos_with_finish()
        
        await message.answer(text, reply_markup=keyboard)
        
        # Логируем информацию о фото
        logger.info(f"Фото получено: {photo_info['file_id']}, размер: {photo_info['width']}x{photo_info['height']}")
    else:
        await message.answer("❌ Ошибка загрузки фото. Попробуйте ещё раз.")

@router.message(F.text == ButtonTexts.NEXT_TO_COMMENT.value, StateFilter(ComplaintStates.uploading_photos))
async def next_to_comment(message: Message, state: FSMContext):
    """Переход к комментарию после фото"""
    await state.set_state(ComplaintStates.entering_comment)
    await message.answer(Messages.ENTER_COMMENT.value, reply_markup=Keyboards.comment_input())

@router.message(F.text == ButtonTexts.FINISH_PHOTOS.value, StateFilter(ComplaintStates.uploading_photos))
async def finish_photos(message: Message, state: FSMContext):
    """Завершение загрузки фото и переход к комментарию"""
    await state.set_state(ComplaintStates.entering_comment)
    await message.answer(Messages.ENTER_COMMENT.value, reply_markup=Keyboards.comment_input())





@router.message(F.text, StateFilter(ComplaintStates.entering_comment))
async def handle_text_comment(message: Message, state: FSMContext):
    """Обработка текстового комментария"""
    # Проверяем на кнопку отмены
    if message.text == ButtonTexts.CANCEL_COMPLAINT.value:
        await cancel_complaint(message, state)
        return
    
    await state.update_data(comment=message.text)
    await show_preview(message, state)


@router.message((F.voice | F.audio), StateFilter(ComplaintStates.entering_comment))
async def handle_voice_comment(message: Message, state: FSMContext):
    """Обработка голосового или аудио комментария"""
    # Показываем индикатор обработки
    processing_msg = await message.answer("🎤 Анализируем аудио...")
    
    try:
        if message.voice:
            file = message.voice
        else:
            file = message.audio

        comment = await media_handler.process_voice_message(message.bot, file)
        
        # Удаляем сообщение об обработке
        await processing_msg.delete()
        
        if comment:
            await state.update_data(comment=comment)
            await show_preview(message, state)
        else:
            await message.answer("❌ Не удалось распознать речь. Попробуйте отправить текстовое сообщение.")
            
    except Exception as e:
        # Удаляем сообщение об обработке в случае ошибки
        await processing_msg.delete()
        await message.answer("❌ Ошибка обработки аудио. Попробуйте отправить текстовое сообщение.")


async def show_preview(message: Message, state: FSMContext):
    """Показ предварительного просмотра"""
    data = await state.get_data()
    
    await state.set_state(ComplaintStates.preview)
    
    photos = data.get('photos', [])
    if photos:
        photos_text = f"\n📷 Фотографий: {len(photos)}"
    else:
        photos_text = "\n📷 Фотографий: ❌"
    
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


@router.message(F.text == ButtonTexts.SAVE.value, StateFilter(ComplaintStates.preview))
async def save_complaint(message: Message, state: FSMContext):
    """Сохранение жалобы"""
    data = await state.get_data()
    
    # Показываем индикатор загрузки
    loading_msg = await message.answer("⏳ Обрабатываем замечание...")
    
    try:
        # Получаем имя сотрудника
        employee = await db.get_employee_by_telegram_id(message.from_user.id)
        employee_name = employee[1] if employee else "unknown"
        
        # Загружаем фото в S3 (если есть)
        photo_urls = []
        photos_data = data.get('photos', [])
        
        if photos_data:
            photo_urls = await media_handler.upload_photos_to_s3(
                message.bot, 
                photos_data, 
                employee_name
            )
        
        # Сохраняем в базу данных
        db_success = await db.add_complaint(
            employee_telegram_id=message.from_user.id,
            category=data['category'],
            master_name=data['master'],
            comment=data['comment'],
            photo_urls=photo_urls
        )
        
        # Сохраняем в Google Sheets
        sheets_success = await sheets_manager.add_complaint(
            category=data['category'],
            master=data['master'],
            comment=data['comment'],
            photo_urls=photo_urls
        )
        
        # Удаляем сообщение с индикатором загрузки
        await loading_msg.delete()
        
        if db_success and sheets_success:
            text = Messages.COMPLAINT_SAVED.value
        elif db_success:
            text = "✅ Замечание сохранено в базу данных!\n⚠️ Ошибка отправки в Google Sheets."
        else:
            text = Messages.COMPLAINT_ERROR.value
        
        keyboard = Keyboards.send_another()
        await message.answer(text, reply_markup=keyboard)
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка сохранения жалобы: {e}")
        await loading_msg.delete()
        await message.answer(Messages.COMPLAINT_ERROR.value, reply_markup=Keyboards.send_another())
        await state.clear()

@router.message(F.text == ButtonTexts.DELETE_AND_RESTART.value, StateFilter(ComplaintStates.preview))
async def restart_complaint(message: Message, state: FSMContext):
    """Перезапуск процесса подачи жалобы"""
    await state.clear()
    await start_complaint_process(message, state)

@router.message(F.text == ButtonTexts.SEND_ANOTHER.value)
async def send_another_complaint(message: Message, state: FSMContext):
    """Отправка ещё одного замечания"""
    await start_complaint_process(message, state)





# === ОБРАБОТЧИК НЕИЗВЕСТНЫХ СООБЩЕНИЙ ===

@router.message()
async def handle_other_messages(message: Message, state: FSMContext):
    """Обработчик прочих сообщений"""
    if message.chat.type != "private":
        return
    
    # Проверяем доступ
    if not await has_access(message.from_user.id):
        await message.answer(Messages.ACCESS_DENIED.value)
        return
    
    # Отладочная информация
    current_state = await state.get_state()
    message_type = "unknown"
    if message.text:
        message_type = "text"
    elif message.voice:
        message_type = "voice"
    elif message.audio:
        message_type = "audio"
    elif message.photo:
        message_type = "photo"
    
    logger.info(f"Необработанное сообщение: тип={message_type}, состояние={current_state}, пользователь={message.from_user.id}")
    
    # Если пользователь в состоянии загрузки фото, но отправил текст
    if current_state == ComplaintStates.uploading_photos:
        await message.answer("📷 Отправьте фотографию или нажмите кнопку для пропуска/перехода к комментарию.")
        return
    
    # Если пользователь в состоянии ввода комментария, но сообщение не обработалось
    if current_state == ComplaintStates.entering_comment:
        if message.voice:
            await message.answer("🎤 Обрабатываю голосовое сообщение...")
            comment = await media_handler.process_voice_message(message.bot, message.voice)
            if comment:
                await state.update_data(comment=comment)
                await show_preview(message, state)
                return
            else:
                await message.answer("❌ Ошибка обработки голосового сообщения. Попробуйте отправить текст.")
                return
        else:
            await message.answer("💬 Отправьте текстовое или голосовое сообщение с комментарием.")
            return
    
    text = "❓ Не понимаю команду.\n\nИспользуйте /start для начала работы с ботом."
    await message.answer(text)