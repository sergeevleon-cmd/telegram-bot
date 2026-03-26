import os
import re

import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "Не найден BOT_TOKEN. Создайте файл .env (или переменную окружения) по примеру .env.example."
    )

bot = telebot.TeleBot(BOT_TOKEN)

PRIVET_RE = re.compile(r"(?i)\bпривет\b")


@bot.message_handler(commands=["start"])
def on_start(message):
    bot.reply_to(message, "Привет! Я бот. Напиши что-нибудь.")


@bot.message_handler(commands=["ping"])
def on_ping(message):
    bot.reply_to(message, "pong")


@bot.message_handler(commands=["help"])
def on_help(message):
    bot.reply_to(message, "/start - старт\n/ping - pong\n/help - помощь")


@bot.message_handler(func=lambda m: PRIVET_RE.search(m.text or ""))
def on_privet_word(message):
    bot.reply_to(message, "Привет-привет!")


if __name__ == "__main__":
    print("[info] Bot started. Polling...")
    bot.infinity_polling()
