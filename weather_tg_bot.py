import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = '7646260204:AAFcJglGznKbfn4agT-v7ZsNImomyUSi-4A'  # Замените на ваш токен бота
ACCUWEATHER_API_KEY = 'Mgtyi9rQKbWGtohSwDE4DW1t38uT2Hzy'  # Замените на ваш AccuWeather API ключ

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def get_weather(city):
    # Получаем ключ города
    location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={ACCUWEATHER_API_KEY}&q={city}"
    logging.info(f"Making request to location API: {location_url}")

    location_response = requests.get(location_url).json()
    logging.info(f"Location response: {location_response}")
    print(location_response)
    city = location_response[0]['LocalizedName']

    if not location_response:
        logging.warning(f"No data found for location: {city}")
        return None

    location_key = location_response[0]['Key']
    logging.info(f"Location key for {city}: {location_key}")

    # Получаем погодные данные
    weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={ACCUWEATHER_API_KEY}"
    logging.info(f"Making request to weather API: {weather_url}")

    weather_response = requests.get(weather_url).json()
    logging.info(f"Weather response: {weather_response}")

    if not weather_response:
        logging.warning(f"No weather data found for location key: {location_key}")
        return None

    return weather_response[0]  # Вернуть первые данные о погоде


@dp.message_handler()
async def send_weather(message: types.Message):
    city = message.text
    # print(city)
    logging.info(f"Received request for weather in city: {city}")

    weather_data = get_weather(city)
    if weather_data is None:
        await message.reply("Не удалось получить данные о погоде. Пожалуйста, проверьте название города.")
    else:
        try:
            print(weather_data)
            city_name = city
            temperature = weather_data['Temperature']['Metric']['Value']
            precipitation = weather_data['PrecipitationType']
            weather_description = weather_data['WeatherText']
            reply_message = (f"Погода в городе {city_name}:\n"
                             f"Температура: {temperature}°C\n"
                             f"Описание погоды: {weather_description.capitalize()}\n"
                             f"Осадки: {precipitation}")
            await message.reply(reply_message)
        except KeyError as e:
            logging.error(f"Error retrieving weather data: {e}")
            print(weather_data)
            await message.reply(f"Ошибка получения данных: отсутствует ключ {e}. Проверьте название города.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)