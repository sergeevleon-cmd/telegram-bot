import os
import requests
import logging
from logging.handlers import RotatingFileHandler

import telebot
from telebot import types
from telebot import apihelper
from dotenv import load_dotenv

from database import Database
from recipes_api import (
    get_random_recipe,
    search_recipe_by_name,
    get_categories,
    get_recipes_by_category,
    get_areas,
    get_recipes_by_area,
    get_recipe_by_id,
    format_recipe_text,
    translate_to_russian
)
from keyboards import (
    create_main_menu,
    create_search_menu,
    create_favorites_menu,
    create_recipe_buttons,
    create_categories_keyboard,
    create_areas_keyboard,
    create_recipe_list_keyboard,
    create_favorite_recipe_buttons
)

os.makedirs("logs", exist_ok=True)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
console_handler.setFormatter(console_formatter)

file_handler = RotatingFileHandler(
    "logs/bot.log",
    maxBytes=5*1024*1024,
    backupCount=3,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(file_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "Не найден BOT_TOKEN. Создайте файл .env (или переменную окружения) по примеру .env.example."
    )

PROXY = os.getenv("PROXY_URL") or os.getenv("PROXY")
if PROXY:
    apihelper.proxy = {'http': PROXY, 'https': PROXY}
    logger.info(f"Using proxy: {PROXY}")
else:
    logger.info("No proxy configured")

logger.info("Initializing bot...")
bot = telebot.TeleBot(BOT_TOKEN)
logger.info("Bot initialized successfully")

logger.info("Initializing database...")
db = Database()
logger.info("Database initialized successfully")

user_states = {}


def send_recipe_with_buttons(chat_id, meal, is_favorite=False):
    """Отправляет рецепт с кнопками"""
    try:
        recipe_text = format_recipe_text(meal)
        markup = create_recipe_buttons(meal["idMeal"], is_favorite)
        
        bot.send_photo(
            chat_id,
            meal["strMealThumb"],
            caption=recipe_text,
            parse_mode="Markdown",
            reply_markup=markup
        )
        return True
    except Exception as e:
        logger.error(f"Error sending recipe: {e}")
        return False


@bot.message_handler(commands=["start"])
def on_start(message):
    logger.info(f"User {message.from_user.id} started bot")
    user_states[message.from_user.id] = None
    markup = create_main_menu()
    bot.send_message(
        message.chat.id,
        "Привет! 🍽️\n\n"
        "Я бот для поиска рецептов!\n"
        "Выбери действие из меню ниже:",
        reply_markup=markup
    )


@bot.message_handler(commands=["menu"])
def on_menu(message):
    user_states[message.from_user.id] = None
    markup = create_main_menu()
    bot.send_message(
        message.chat.id,
        "Главное меню:",
        reply_markup=markup
    )


@bot.message_handler(commands=["help"])
def on_help(message):
    bot.reply_to(
        message,
        "🍽️ *Бот для поиска рецептов*\n\n"
        "/start - запустить бота\n"
        "/menu - главное меню\n"
        "/help - помощь\n\n"
        "Используйте кнопки меню для навигации!",
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: m.text == "🔍 Поиск рецептов")
def show_search_menu(message):
    logger.info(f"User {message.from_user.id} opened search menu")
    user_states[message.from_user.id] = None
    markup = create_search_menu()
    bot.send_message(
        message.chat.id,
        "🔍 *Поиск рецептов*\n\nВыберите способ поиска:",
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: m.text == "⭐ Мои рецепты")
def show_favorites_menu(message):
    logger.info(f"User {message.from_user.id} opened favorites menu")
    user_states[message.from_user.id] = None
    markup = create_favorites_menu()
    bot.send_message(
        message.chat.id,
        "⭐ *Мои рецепты*\n\nУправление избранными рецептами:",
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: m.text == "⬅️ Назад в меню")
def back_to_main_menu(message):
    user_states[message.from_user.id] = None
    markup = create_main_menu()
    bot.send_message(
        message.chat.id,
        "Главное меню:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "🎲 Случайный рецепт")
def send_random_recipe_handler(message):
    logger.info(f"User {message.from_user.id} requested random recipe")
    try:
        bot.send_chat_action(message.chat.id, "upload_photo")
        meal = get_random_recipe()
        
        if meal:
            is_fav = db.is_favorite(message.from_user.id, meal["idMeal"])
            send_recipe_with_buttons(message.chat.id, meal, is_fav)
            logger.info("Random recipe sent successfully")
        else:
            bot.reply_to(message, "Не удалось получить рецепт 😿")
            logger.warning("Empty response from recipe API")
    except Exception as e:
        logger.error(f"Error getting random recipe: {e}")
        bot.reply_to(message, f"Ошибка при получении рецепта: {str(e)}")


@bot.message_handler(func=lambda m: m.text == "📂 По категориям")
def show_categories(message):
    logger.info(f"User {message.from_user.id} requested categories")
    try:
        bot.send_chat_action(message.chat.id, "typing")
        categories = get_categories()
        
        if categories:
            markup = create_categories_keyboard(categories)
            bot.send_message(
                message.chat.id,
                "📂 *Выберите категорию:*",
                reply_markup=markup,
                parse_mode="Markdown"
            )
            logger.info("Categories sent successfully")
        else:
            bot.reply_to(message, "Не удалось получить категории 😿")
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        bot.reply_to(message, f"Ошибка: {str(e)}")


@bot.message_handler(func=lambda m: m.text == "🌍 По кухням мира")
def show_areas(message):
    logger.info(f"User {message.from_user.id} requested areas")
    try:
        bot.send_chat_action(message.chat.id, "typing")
        areas = get_areas()
        
        if areas:
            markup = create_areas_keyboard(areas)
            bot.send_message(
                message.chat.id,
                "🌍 *Выберите кухню мира:*",
                reply_markup=markup,
                parse_mode="Markdown"
            )
            logger.info("Areas sent successfully")
        else:
            bot.reply_to(message, "Не удалось получить список кухонь 😿")
    except Exception as e:
        logger.error(f"Error getting areas: {e}")
        bot.reply_to(message, f"Ошибка: {str(e)}")


@bot.message_handler(func=lambda m: m.text == "🔤 По названию")
def ask_recipe_name(message):
    logger.info(f"User {message.from_user.id} wants to search by name")
    user_states[message.from_user.id] = "waiting_recipe_name"
    bot.send_message(
        message.chat.id,
        "🔤 Введите название блюда (на английском):\n\n"
        "Например: _pasta_, _chicken_, _cake_",
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: m.text == "📋 Показать избранное")
def show_favorites(message):
    logger.info(f"User {message.from_user.id} requested favorites")
    try:
        favorites = db.get_favorites(message.from_user.id)
        
        if not favorites:
            bot.send_message(
                message.chat.id,
                "⭐ У вас пока нет избранных рецептов.\n\n"
                "Найдите рецепты через поиск и добавьте их в избранное!"
            )
            return
        
        bot.send_message(
            message.chat.id,
            f"⭐ *Ваши избранные рецепты* ({len(favorites)}):\n\n"
            "Загружаю...",
            parse_mode="Markdown"
        )
        
        for meal_id, meal_name, meal_thumb, added_at in favorites:
            meal = get_recipe_by_id(meal_id)
            if meal:
                send_recipe_with_buttons(message.chat.id, meal, is_favorite=True)
            else:
                markup = types.InlineKeyboardMarkup()
                btn = types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"remove_{meal_id}")
                markup.add(btn)
                bot.send_photo(
                    message.chat.id,
                    meal_thumb,
                    caption=f"🍽️ *{meal_name}*\n\n_Детали недоступны_",
                    parse_mode="Markdown",
                    reply_markup=markup
                )
        
        logger.info(f"Sent {len(favorites)} favorite recipes")
    except Exception as e:
        logger.error(f"Error showing favorites: {e}")
        bot.reply_to(message, f"Ошибка при получении избранного: {str(e)}")


@bot.message_handler(func=lambda m: m.text == "🗑️ Очистить избранное")
def clear_favorites(message):
    logger.info(f"User {message.from_user.id} wants to clear favorites")
    try:
        count = db.clear_favorites(message.from_user.id)
        
        if count > 0:
            bot.send_message(
                message.chat.id,
                f"🗑️ Удалено {count} рецептов из избранного"
            )
        else:
            bot.send_message(
                message.chat.id,
                "У вас нет избранных рецептов"
            )
        
        logger.info(f"Cleared {count} favorites")
    except Exception as e:
        logger.error(f"Error clearing favorites: {e}")
        bot.reply_to(message, f"Ошибка: {str(e)}")


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "waiting_recipe_name")
def search_by_name(message):
    logger.info(f"User {message.from_user.id} searching for: {message.text}")
    user_states[message.from_user.id] = None
    
    try:
        bot.send_chat_action(message.chat.id, "typing")
        recipes = search_recipe_by_name(message.text)
        
        if not recipes:
            bot.send_message(
                message.chat.id,
                "😿 Рецепты не найдены.\n\n"
                "Попробуйте другое название или используйте английский язык."
            )
            return
        
        if len(recipes) == 1:
            meal = recipes[0]
            is_fav = db.is_favorite(message.from_user.id, meal["idMeal"])
            send_recipe_with_buttons(message.chat.id, meal, is_fav)
        else:
            markup = create_recipe_list_keyboard(recipes, "recipe")
            bot.send_message(
                message.chat.id,
                f"🔍 Найдено рецептов: *{len(recipes)}*\n\n"
                "Выберите рецепт:",
                reply_markup=markup,
                parse_mode="Markdown"
            )
        
        logger.info(f"Found {len(recipes)} recipes")
    except Exception as e:
        logger.error(f"Error searching recipes: {e}")
        bot.reply_to(message, f"Ошибка при поиске: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def handle_category(call):
    category = call.data.replace("cat_", "")
    logger.info(f"User {call.from_user.id} selected category: {category}")
    
    try:
        bot.answer_callback_query(call.id, f"Загружаю {category}...")
        recipes = get_recipes_by_category(category)
        
        if recipes:
            markup = create_recipe_list_keyboard(recipes, "recipe")
            bot.send_message(
                call.message.chat.id,
                f"📂 *{category}* ({len(recipes)} рецептов)\n\n"
                "Выберите рецепт:",
                reply_markup=markup,
                parse_mode="Markdown"
            )
        else:
            bot.send_message(call.message.chat.id, "Рецепты не найдены 😿")
    except Exception as e:
        logger.error(f"Error getting recipes by category: {e}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("area_"))
def handle_area(call):
    area = call.data.replace("area_", "")
    logger.info(f"User {call.from_user.id} selected area: {area}")
    
    try:
        bot.answer_callback_query(call.id, f"Загружаю {area}...")
        recipes = get_recipes_by_area(area)
        
        if recipes:
            markup = create_recipe_list_keyboard(recipes, "recipe")
            bot.send_message(
                call.message.chat.id,
                f"🌍 *{area}* ({len(recipes)} рецептов)\n\n"
                "Выберите рецепт:",
                reply_markup=markup,
                parse_mode="Markdown"
            )
        else:
            bot.send_message(call.message.chat.id, "Рецепты не найдены 😿")
    except Exception as e:
        logger.error(f"Error getting recipes by area: {e}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("recipe_"))
def show_recipe_details(call):
    meal_id = call.data.replace("recipe_", "")
    logger.info(f"User {call.from_user.id} selected recipe: {meal_id}")
    
    try:
        bot.answer_callback_query(call.id)
        meal = get_recipe_by_id(meal_id)
        
        if meal:
            is_fav = db.is_favorite(call.from_user.id, meal["idMeal"])
            send_recipe_with_buttons(call.message.chat.id, meal, is_fav)
        else:
            bot.send_message(call.message.chat.id, "Рецепт не найден 😿")
    except Exception as e:
        logger.error(f"Error showing recipe details: {e}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("fav_"))
def add_to_favorites(call):
    meal_id = call.data.replace("fav_", "")
    logger.info(f"User {call.from_user.id} adding to favorites: {meal_id}")
    
    try:
        meal = get_recipe_by_id(meal_id)
        
        if meal:
            meal_name_ru = translate_to_russian(meal["strMeal"])
            success = db.add_favorite(
                call.from_user.id,
                meal["idMeal"],
                meal_name_ru,
                meal["strMealThumb"]
            )
            
            if success:
                bot.answer_callback_query(call.id, "✅ Добавлено в избранное!", show_alert=True)
                
                new_markup = create_recipe_buttons(meal_id, is_favorite=True)
                bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=new_markup
                )
                logger.info("Recipe added to favorites")
            else:
                bot.answer_callback_query(call.id, "⚠️ Рецепт уже в избранном", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Ошибка при добавлении", show_alert=True)
    except Exception as e:
        logger.error(f"Error adding to favorites: {e}")
        bot.answer_callback_query(call.id, "Ошибка", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("remove_"))
def remove_from_favorites(call):
    meal_id = call.data.replace("remove_", "")
    logger.info(f"User {call.from_user.id} removing from favorites: {meal_id}")
    
    try:
        success = db.remove_favorite(call.from_user.id, meal_id)
        
        if success:
            bot.answer_callback_query(call.id, "🗑️ Удалено из избранного", show_alert=True)
            
            try:
                new_markup = create_recipe_buttons(meal_id, is_favorite=False)
                bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=new_markup
                )
            except:
                pass
            
            logger.info("Recipe removed from favorites")
        else:
            bot.answer_callback_query(call.id, "⚠️ Рецепт не найден в избранном", show_alert=True)
    except Exception as e:
        logger.error(f"Error removing from favorites: {e}")
        bot.answer_callback_query(call.id, "Ошибка", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data == "random")
def send_another_random(call):
    logger.info(f"User {call.from_user.id} requested another random recipe")
    try:
        bot.answer_callback_query(call.id, "Загружаю новый рецепт...")
        meal = get_random_recipe()
        
        if meal:
            is_fav = db.is_favorite(call.from_user.id, meal["idMeal"])
            send_recipe_with_buttons(call.message.chat.id, meal, is_fav)
        else:
            bot.answer_callback_query(call.id, "Ошибка при загрузке", show_alert=True)
    except Exception as e:
        logger.error(f"Error getting another random recipe: {e}")
        bot.answer_callback_query(call.id, "Ошибка", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_favorites")
def back_to_favorites(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "⭐ Используйте кнопку '📋 Показать избранное' для просмотра"
    )


if __name__ == "__main__":
    logger.info("Bot started. Starting polling...")
    try:
        bot.infinity_polling(skip_pending=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        raise
