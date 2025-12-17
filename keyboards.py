from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import GROUPS, GROUPS_PER_PAGE


def get_groups_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """
    Creates a paginated inline keyboard with groups.
    
    Args:
        page: Current page number (0-indexed)
    
    Returns:
        InlineKeyboardMarkup with group buttons and navigation
    """
    total_pages = (len(GROUPS) - 1) // GROUPS_PER_PAGE + 1
    start_idx = page * GROUPS_PER_PAGE
    end_idx = min(start_idx + GROUPS_PER_PAGE, len(GROUPS))
    
    buttons = []
    
    # Add group buttons (2 per row)
    current_groups = GROUPS[start_idx:end_idx]
    for i in range(0, len(current_groups), 2):
        row = []
        row.append(InlineKeyboardButton(
            text=current_groups[i],
            callback_data=f"group:{current_groups[i]}"
        ))
        if i + 1 < len(current_groups):
            row.append(InlineKeyboardButton(
                text=current_groups[i + 1],
                callback_data=f"group:{current_groups[i + 1]}"
            ))
        buttons.append(row)
    
    # Add navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"page:{page - 1}"
        ))
    
    nav_buttons.append(InlineKeyboardButton(
        text=f"{page + 1}/{total_pages}",
        callback_data="ignore"
    ))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(
            text="Вперёд ▶️",
            callback_data=f"page:{page + 1}"
        ))
    
    buttons.append(nav_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_date_keyboard() -> InlineKeyboardMarkup:
    """
    Creates inline keyboard with today/tomorrow buttons.
    
    Returns:
        InlineKeyboardMarkup with date selection buttons
    """
    buttons = [
        [
            InlineKeyboardButton(text="📅 Сегодня", callback_data="date:today"),
            InlineKeyboardButton(text="📅 Завтра", callback_data="date:tomorrow")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад к выбору группы", callback_data="back_to_groups")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard():
    """
    Get keyboard with back buttons.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 К выбору группы", callback_data="back_to_groups"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")
        ]
    ])
