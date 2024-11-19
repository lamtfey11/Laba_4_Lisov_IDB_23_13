import telebot
import logging
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен Telegram-бота и OpenWeather API
TELEGRAM_API_TOKEN = "7594507179:AAGRbNwpTE08yRSCx8L_fDtyb5fBo-elUBk"  # ТГ токен
WEATHER_API_KEY = "eeaea6e6965d4b11c6da0f3f98eb4f80"  #API-ключ

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

if __name__ == "__main__":
    bot.infinity_polling()