from telebot import types


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


def create_recipe_buttons(meal_id, is_favorite=False):
    """Создает inline кнопки под рецептом"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    if is_favorite:
        btn1 = types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"remove_{meal_id}")
    else:
        btn1 = types.InlineKeyboardButton("⭐ В избранное", callback_data=f"fav_{meal_id}")
    
    btn2 = types.InlineKeyboardButton("🔄 Еще рецепт", callback_data="random")
    markup.add(btn1, btn2)
    return markup


def create_categories_keyboard(categories):
    """Создает inline клавиатуру с категориями"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    for cat in categories[:12]:
        btn = types.InlineKeyboardButton(
            cat["strCategory"],
            callback_data=f"cat_{cat['strCategory']}"
        )
        markup.add(btn)
    
    return markup


def create_areas_keyboard(areas):
    """Создает inline клавиатуру с кухнями мира"""
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    buttons = []
    for area in areas[:18]:
        btn = types.InlineKeyboardButton(
            area["strArea"],
            callback_data=f"area_{area['strArea']}"
        )
        buttons.append(btn)
    
    for i in range(0, len(buttons), 3):
        markup.row(*buttons[i:i+3])
    
    return markup


def create_recipe_list_keyboard(recipes, prefix="recipe"):
    """Создает inline клавиатуру со списком рецептов"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for recipe in recipes[:10]:
        btn = types.InlineKeyboardButton(
            recipe["strMeal"],
            callback_data=f"{prefix}_{recipe['idMeal']}"
        )
        markup.add(btn)
    
    return markup


def create_favorite_recipe_buttons(meal_id):
    """Создает inline кнопки для избранного рецепта"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"remove_{meal_id}")
    btn2 = types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_favorites")
    markup.add(btn1, btn2)
    return markup
