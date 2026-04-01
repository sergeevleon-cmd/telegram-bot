import os
import re
import requests
import logging

import telebot
from telebot import types
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "Не найден BOT_TOKEN. Создайте файл .env (или переменную окружения) по примеру .env.example."
    )

logger.info("Initializing bot...")
bot = telebot.TeleBot(BOT_TOKEN)
logger.info("Bot initialized successfully")

PRIVET_RE = re.compile(r"(?i)\bпривет\b")


def translate_to_russian(text):
    """Переводит текст на русский язык через бесплатный API"""
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
    """Создает главное меню с кнопками"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🐱 Фото кота")
    btn2 = types.KeyboardButton("🐶 Факт о собаке")
    btn3 = types.KeyboardButton("🦊 Фото лисицы")
    btn4 = types.KeyboardButton("💭 Факт о кошке")
    markup.add(btn1, btn2, btn3, btn4)
    return markup


@bot.message_handler(commands=["start"])
def on_start(message):
    logger.info(f"User {message.from_user.id} started bot")
    markup = create_main_menu()
    bot.send_message(
        message.chat.id,
        "Привет! 🎉\n\nЯ бот с милыми животными!\n"
        "Выбери действие из меню ниже:",
        reply_markup=markup
    )


@bot.message_handler(commands=["menu"])
def on_menu(message):
    markup = create_main_menu()
    bot.send_message(
        message.chat.id,
        "Главное меню:",
        reply_markup=markup
    )


@bot.message_handler(commands=["ping"])
def on_ping(message):
    bot.reply_to(message, "pong")


@bot.message_handler(commands=["help"])
def on_help(message):
    bot.reply_to(
        message,
        "/start - запустить бота и показать меню\n"
        "/menu - показать меню\n"
        "/ping - проверка связи\n"
        "/help - помощь"
    )


@bot.message_handler(func=lambda m: m.text == "🐱 Фото кота")
def send_cat_photo(message):
    logger.info(f"User {message.from_user.id} requested cat photo")
    try:
        bot.send_chat_action(message.chat.id, "upload_photo")
        response = requests.get("https://api.thecatapi.com/v1/images/search", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            cat_url = data[0]["url"]
            bot.send_photo(message.chat.id, cat_url, caption="Вот твой котик! 🐱")
            logger.info("Cat photo sent successfully")
        else:
            bot.reply_to(message, "Не удалось получить фото кота 😿")
            logger.warning("Empty response from cat API")
    except Exception as e:
        logger.error(f"Error getting cat photo: {e}")
        bot.reply_to(message, f"Ошибка при получении фото: {str(e)}")


@bot.message_handler(func=lambda m: m.text == "💭 Факт о кошке")
def send_cat_fact(message):
    logger.info(f"User {message.from_user.id} requested cat fact")
    try:
        bot.send_chat_action(message.chat.id, "typing")
        response = requests.get("https://catfact.ninja/fact", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "fact" in data:
            fact_en = data['fact']
            fact_ru = translate_to_russian(fact_en)
            bot.reply_to(message, f"💭 Факт о кошках:\n\n{fact_ru}")
            logger.info("Cat fact sent successfully")
        else:
            bot.reply_to(message, "Не удалось получить факт 😿")
            logger.warning("Empty response from cat fact API")
    except Exception as e:
        logger.error(f"Error getting cat fact: {e}")
        bot.reply_to(message, f"Ошибка при получении факта: {str(e)}")


@bot.message_handler(func=lambda m: m.text == "🐶 Факт о собаке")
def send_dog_fact(message):
    logger.info(f"User {message.from_user.id} requested dog fact")
    try:
        bot.send_chat_action(message.chat.id, "typing")
        response = requests.get("https://dogapi.dog/api/v2/facts", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "data" in data and len(data["data"]) > 0:
            fact_en = data["data"][0]["attributes"]["body"]
            fact_ru = translate_to_russian(fact_en)
            bot.reply_to(message, f"🐶 Факт о собаках:\n\n{fact_ru}")
            logger.info("Dog fact sent successfully")
        else:
            bot.reply_to(message, "Не удалось получить факт 🐕")
            logger.warning("Empty response from dog fact API")
    except Exception as e:
        logger.error(f"Error getting dog fact: {e}")
        bot.reply_to(message, f"Ошибка при получении факта: {str(e)}")


@bot.message_handler(func=lambda m: m.text == "🦊 Фото лисицы")
def send_fox_photo(message):
    logger.info(f"User {message.from_user.id} requested fox photo")
    try:
        bot.send_chat_action(message.chat.id, "upload_photo")
        response = requests.get("https://randomfox.ca/floof/", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "image" in data:
            fox_url = data["image"]
            bot.send_photo(message.chat.id, fox_url, caption="Вот твоя лисичка! 🦊")
            logger.info("Fox photo sent successfully")
        else:
            bot.reply_to(message, "Не удалось получить фото лисы 🦊")
            logger.warning("Empty response from fox API")
    except Exception as e:
        logger.error(f"Error getting fox photo: {e}")
        bot.reply_to(message, f"Ошибка при получении фото: {str(e)}")


@bot.message_handler(func=lambda m: PRIVET_RE.search(m.text or ""))
def on_privet_word(message):
    bot.reply_to(message, "Привет-привет!")


if __name__ == "__main__":
    logger.info("Bot started. Starting polling...")
    try:
        bot.infinity_polling(skip_pending=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        raise
