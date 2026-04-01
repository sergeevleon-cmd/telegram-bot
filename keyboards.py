from telebot import types
import requests
import logging

logger = logging.getLogger(__name__)


def translate_to_russian(text):
    """Переводит текст на русский язык"""
    if not text or not text.strip():
        return text
    
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "en",
            "tl": "ru",
            "dt": "t",
            "q": text
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            result = response.json()
            translated = result[0][0][0]
            return translated
        return text
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
        return text


def create_main_menu():
    """Создает главное меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("🔍 Поиск рецептов")
    btn2 = types.KeyboardButton("⭐ Мои рецепты")
    markup.add(btn1, btn2)
    return markup


def create_search_menu():
    """Создает меню поиска рецептов"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🎲 Случайный рецепт")
    btn2 = types.KeyboardButton("📂 По категориям")
    btn3 = types.KeyboardButton("🌍 По кухням мира")
    btn4 = types.KeyboardButton("🔤 По названию")
    btn_back = types.KeyboardButton("⬅️ Назад в меню")
    markup.add(btn1, btn2, btn3, btn4, btn_back)
    return markup


def create_favorites_menu():
    """Создает меню избранного"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("📋 Показать избранное")
    btn2 = types.KeyboardButton("🗑️ Очистить избранное")
    btn_back = types.KeyboardButton("⬅️ Назад в меню")
    markup.add(btn1, btn2, btn_back)
    return markup


def create_recipe_buttons(meal_id, is_favorite=False, rating=0):
    """Создает inline кнопки под рецептом с рейтингом в одну строку"""
    markup = types.InlineKeyboardMarkup()
    
    if is_favorite:
        rating_buttons = []
        for r in range(1, 6):
            if r <= rating:
                label = "⭐"
            else:
                label = "☆"
            
            btn = types.InlineKeyboardButton(
                label,
                callback_data=f"rate_{meal_id}_{r}"
            )
            rating_buttons.append(btn)
        
        markup.row(*rating_buttons)
        
        btn1 = types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"remove_{meal_id}")
        btn2 = types.InlineKeyboardButton("🔄 Еще рецепт", callback_data="random")
        markup.row(btn1, btn2)
    else:
        btn1 = types.InlineKeyboardButton("⭐ В избранное", callback_data=f"fav_{meal_id}")
        btn2 = types.InlineKeyboardButton("🔄 Еще рецепт", callback_data="random")
        markup.row(btn1, btn2)
    
    return markup


def create_categories_keyboard(categories):
    """Создает inline клавиатуру с категориями на русском"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    for cat in categories[:12]:
        category_name = cat["strCategory"]
        category_name_ru = translate_to_russian(category_name)
        btn = types.InlineKeyboardButton(
            category_name_ru,
            callback_data=f"cat_{category_name}"
        )
        markup.add(btn)
    
    return markup


def create_areas_keyboard(areas):
    """Создает inline клавиатуру с кухнями мира на русском"""
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    buttons = []
    for area in areas[:18]:
        area_name = area["strArea"]
        area_name_ru = translate_to_russian(area_name)
        btn = types.InlineKeyboardButton(
            area_name_ru,
            callback_data=f"area_{area_name}"
        )
        buttons.append(btn)
    
    for i in range(0, len(buttons), 3):
        markup.row(*buttons[i:i+3])
    
    return markup


def create_recipe_list_keyboard(recipes, prefix="recipe"):
    """Создает inline клавиатуру со списком рецептов на русском"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for recipe in recipes[:10]:
        recipe_name_ru = translate_to_russian(recipe["strMeal"])
        btn = types.InlineKeyboardButton(
            recipe_name_ru,
            callback_data=f"{prefix}_{recipe['idMeal']}"
        )
        markup.add(btn)
    
    return markup


def create_rating_keyboard(meal_id, current_rating=0):
    """Создает клавиатуру для выбора рейтинга с визуализацией"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for rating in range(5, 0, -1):
        filled = "⭐" * rating
        empty = "☆" * (5 - rating)
        label = f"{rating} {filled}{empty}"
        
        btn = types.InlineKeyboardButton(
            label,
            callback_data=f"rate_{meal_id}_{rating}"
        )
        markup.add(btn)
    
    return markup


def create_favorite_recipe_buttons(meal_id, rating=0):
    """Создает inline кнопки для избранного рецепта"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    if rating > 0:
        btn_rating = types.InlineKeyboardButton(
            f"{'⭐' * rating} Изменить оценку",
            callback_data=f"change_rating_{meal_id}"
        )
        markup.add(btn_rating)
    else:
        btn_rating = types.InlineKeyboardButton(
            "⭐ Оценить рецепт",
            callback_data=f"change_rating_{meal_id}"
        )
        markup.add(btn_rating)
    
    btn1 = types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"remove_{meal_id}")
    btn2 = types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_favorites")
    markup.add(btn1, btn2)
    return markup
