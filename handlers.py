from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import get_groups_keyboard, get_date_keyboard, get_back_keyboard
from parser import fetch_schedule, format_schedule
from database import Database


# Initialize database
db = Database()


# Define FSM states
class ScheduleStates(StatesGroup):
    waiting_for_group = State()
    group_selected = State()
    setting_default_group = State()


# Create router
router = Router()


def get_main_menu_keyboard(has_default_group: bool = False):
    """Get main menu keyboard with My Group button if user has a default group."""
    buttons = []
    
    if has_default_group:
        buttons.append([InlineKeyboardButton(text="📚 Моя группа", callback_data="my_group")])
    
    buttons.extend([
        [InlineKeyboardButton(text="🔍 Выбрать группу", callback_data="select_group")],
        [InlineKeyboardButton(text="⚙️ Установить мою группу", callback_data="set_default_group")],
        [InlineKeyboardButton(text="🔔 Уведомления (вкл/выкл)", callback_data="toggle_notifications")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Handle /start command - show main menu.
    """
    await state.clear()
    
    user_id = message.from_user.id
    default_group = db.get_default_group(user_id)
    
    welcome_text = "👋 Привет! Я бот для просмотра расписания ЛНТРТ.\n\n"
    
    if default_group:
        welcome_text += f"📚 Ваша группа: **{default_group}**\n\n"
    
    welcome_text += "Выберите действие:"
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(has_default_group=bool(default_group)),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("page:"))
async def handle_page_navigation(callback: CallbackQuery):
    """
    Handle pagination for group selection.
    """
    page = int(callback.data.split(":")[1])
    
    await callback.message.edit_reply_markup(
        reply_markup=get_groups_keyboard(page=page)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("group:"))
async def handle_group_selection(callback: CallbackQuery, state: FSMContext):
    """
    Handle group selection - save to state and show date options or save as default.
    """
    group = callback.data.split(":")[1]
    
    # Check current state
    current_state = await state.get_state()
    
    if current_state == ScheduleStates.setting_default_group:
        # User is setting their default group
        user_id = callback.from_user.id
        db.set_default_group(user_id, group)
        
        await state.clear()
        
        await callback.message.edit_text(
            f"✅ Группа **{group}** установлена по умолчанию!\n\n"
            "Теперь вы можете быстро получать расписание через кнопку \"Моя группа\"\n\n"
            "Выберите действие:",
            reply_markup=get_main_menu_keyboard(has_default_group=True),
            parse_mode="Markdown"
        )
        await callback.answer("Группа сохранена!")
    else:
        # Regular group selection for viewing schedule
        # Save selected group to state
        await state.update_data(group=group)
        await state.set_state(ScheduleStates.group_selected)
        
        await callback.message.edit_text(
            f"✅ Вы выбрали группу: {group}\n\n"
            "📅 Выберите день:",
            reply_markup=get_date_keyboard()
        )
        await callback.answer()


@router.callback_query(F.data.startswith("date:"))
async def handle_date_selection(callback: CallbackQuery, state: FSMContext):
    """
    Handle date selection - fetch and send schedule.
    """
    date_type = callback.data.split(":")[1]
    days_offset = 0 if date_type == "today" else 1
    
    # Get selected group from state
    user_data = await state.get_data()
    group = user_data.get("group")
    
    if not group:
        await callback.answer("❌ Группа не выбрана. Начните с /start", show_alert=True)
        return
    
    # Show loading message
    await callback.answer("⏳ Загружаю расписание...")
    
    # Fetch schedule
    lessons = fetch_schedule(group, days_offset)
    
    if lessons is None:
        await callback.message.answer(
            "❌ Не удалось загрузить расписание. Попробуйте позже.",
            reply_markup=get_back_keyboard()
        )
    else:
        # Format and send schedule
        schedule_text = format_schedule(lessons, group, days_offset)
        
        await callback.message.answer(
            schedule_text,
            reply_markup=get_back_keyboard()
        )




@router.callback_query(F.data == "my_group")
async def handle_my_group(callback: CallbackQuery, state: FSMContext):
    """
    Show schedule for user's default group.
    """
    user_id = callback.from_user.id
    group = db.get_default_group(user_id)
    
    if not group:
        await callback.answer("❌ У вас не установлена группа по умолчанию", show_alert=True)
        return
    
    # Save group to state
    await state.update_data(group=group)
    await state.set_state(ScheduleStates.group_selected)
    
    await callback.message.edit_text(
        f"✅ Группа: {group}\n\n"
        "📅 Выберите день:",
        reply_markup=get_date_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "select_group")
async def handle_select_group(callback: CallbackQuery, state: FSMContext):
    """
    Show group selection menu.
    """
    await state.set_state(ScheduleStates.waiting_for_group)
    
    await callback.message.edit_text(
        "📚 Выберите группу:",
        reply_markup=get_groups_keyboard(page=0)
    )
    await callback.answer()


@router.callback_query(F.data == "set_default_group")
async def handle_set_default_group(callback: CallbackQuery, state: FSMContext):
    """
    Start process to set default group.
    """
    await state.set_state(ScheduleStates.setting_default_group)
    
    await callback.message.edit_text(
        "⚙️ **Установка группы по умолчанию**\n\n"
        "Выберите вашу группу:",
        reply_markup=get_groups_keyboard(page=0),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_notifications")
async def handle_toggle_notifications(callback: CallbackQuery):
    """
    Toggle notifications on/off.
    """
    user_id = callback.from_user.id
    current_state = db.get_notifications_enabled(user_id)
    new_state = not current_state
    
    db.set_notifications(user_id, new_state)
    
    status_emoji = "🔔" if new_state else "🔕"
    status_text = "включены" if new_state else "выключены"
    
    # Check if user has default group
    default_group = db.get_default_group(user_id)
    
    message = f"{status_emoji} Уведомления **{status_text}**\n\n"
    
    if new_state and not default_group:
        message += "⚠️ Для получения уведомлений установите группу по умолчанию!\n\n"
    elif new_state:
        message += f"✅ Каждый день в 18:00 вы будете получать расписание на завтра для группы **{default_group}**\n\n"
    
    message += "Выберите действие:"
    
    await callback.message.edit_text(
        message,
        reply_markup=get_main_menu_keyboard(has_default_group=bool(default_group)),
        parse_mode="Markdown"
    )
    await callback.answer(f"Уведомления {status_text}")


@router.callback_query(F.data == "back_to_main")
async def handle_back_to_main(callback: CallbackQuery, state: FSMContext):
    """
    Return to main menu.
    """
    await state.clear()
    
    user_id = callback.from_user.id
    default_group = db.get_default_group(user_id)
    
    welcome_text = "📚 Главное меню\n\n"
    
    if default_group:
        welcome_text += f"Ваша группа: **{default_group}**\n\n"
    
    welcome_text += "Выберите действие:"
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(has_default_group=bool(default_group)),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_groups")
async def handle_back_to_groups(callback: CallbackQuery, state: FSMContext):
    """
    Handle back button - return to group selection.
    """
    await state.set_state(ScheduleStates.waiting_for_group)
    
    await callback.message.edit_text(
        "📚 Выберите свою группу:",
        reply_markup=get_groups_keyboard(page=0)
    )
    await callback.answer()


@router.callback_query(F.data == "ignore")
async def handle_ignore(callback: CallbackQuery):
    """
    Handle ignored callbacks (like page counter button).
    """
    await callback.answer()
