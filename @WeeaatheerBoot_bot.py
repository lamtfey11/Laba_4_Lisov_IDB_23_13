import telebot
import logging
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен Telegram-бота и OpenWeather API
TELEGRAM_API_TOKEN = "7594507179:AAGRbNwpTE08yRSCx8L_fDtyb5fBo-elUBk"  # Замените на ваш токен
WEATHER_API_KEY = "eeaea6e6965d4b11c6da0f3f98eb4f80"  # Замените на ваш API-ключ

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

# Переменные для хранения пользовательских настроек
user_units = {}  # Словарь {user_id: "metric"/"imperial"} для хранения единиц измерения
user_city = {}  # Словарь {user_id: "city"} для хранения города пользователя

# Клавиатура
main_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row("Сменить единицы измерения", "Мой город", "Погода в моем городе")

@bot.message_handler(commands=["start"])
def start_command(message):
    """Приветствие пользователя при старте."""
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для получения погоды. Напишите название города, чтобы узнать погоду, "
        "или воспользуйтесь кнопками ниже.",
        reply_markup=main_keyboard
    )

@bot.message_handler(func=lambda message: message.text == "Сменить единицы измерения")
def change_units(message):
    """Сменить единицы измерения температуры."""
    user_id = message.from_user.id
    current_unit = user_units.get(user_id, "metric")
    new_unit = "imperial" if current_unit == "metric" else "metric"
    user_units[user_id] = new_unit
    unit_name = "Фаренгейт" if new_unit == "imperial" else "Цельсий"
    bot.send_message(message.chat.id, f"Единицы измерения изменены на: {unit_name}")

@bot.message_handler(func=lambda message: message.text == "Мой город")
def set_city(message):
    """Запрашивает у пользователя город для сохранения."""
    bot.send_message(message.chat.id, "Введите название города, который вы хотите сохранить:")

    # Устанавливаем состояние ожидания ввода города
    user_city[message.from_user.id] = "awaiting_city"

@bot.message_handler(func=lambda message: message.text == "Погода в моем городе")
def weather_in_saved_city(message):
    """Выводит погоду для сохраненного города."""
    user_id = message.from_user.id
    city = user_city.get(user_id)
    if city and city != "awaiting_city":
        get_weather_for_city(message, city)
    else:
        bot.send_message(message.chat.id, "Вы ещё не сохранили свой город. Нажмите 'Мой город', чтобы сохранить его.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Обрабатывает ввод текста."""
    user_id = message.from_user.id

    # Если ожидается ввод города для сохранения
    if user_city.get(user_id) == "awaiting_city":
        city = message.text.strip()
        user_city[user_id] = city
        bot.send_message(message.chat.id, f"Ваш город сохранён: {city}.")
    else:
        # Пользователь ввёл город для мгновенного запроса погоды
        get_weather_for_city(message, message.text.strip())

def get_weather_for_city(message, city):
    """Получить погоду для указанного города."""
    user_id = message.from_user.id
    units = user_units.get(user_id, "metric")  # Использовать сохранённые настройки пользователя

    # Формирование URL для API
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units={units}&lang=ru"

    try:
        response = requests.get(url, timeout=10)  # запрос с тайм-аутом
        if response.status_code == 200:
            data = response.json()  # Преобразование ответа в JSON
            weather = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            unit_name = "°C" if units == "metric" else "°F"
            wind_unit = "м/с" if units == "metric" else "миль/ч"

            # Отправляем ответ с погодой
            bot.send_message(
                message.chat.id,
                f"Погода в {city}:\n"
                f"🌡 Температура: {temp}{unit_name}\n"
                f"🤗 Ощущается как: {feels_like}{unit_name}\n"
                f"💧 Влажность: {humidity}%\n"
                f"🌬 Скорость ветра: {wind_speed} {wind_unit}\n"
                f"☁️ Описание: {weather}"
            )
        else:
            bot.send_message(
                message.chat.id, f"Не удалось получить данные о погоде для города '{city}'. Проверьте название и попробуйте снова."
            )
    except requests.exceptions.RequestException:
        bot.send_message(message.chat.id, "Произошла ошибка при попытке получить данные о погоде. Попробуйте ещё раз.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    bot.infinity_polling()