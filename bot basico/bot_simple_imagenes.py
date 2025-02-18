import telebot
from telebot import types
import requests

# Conexión con el bot
TOKEN = '7866951841:AAFhmJurjHhVNDaSsn8k80aqzLnh1saYMB8'
API_KEY = '6ae5b9fb46b1cd58a6796c0b041b4c5b'
bot = telebot.TeleBot(TOKEN)

BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?'

# Métodos

def get_weather(city_name):
    """
    Obtiene el clima de una ciudad utilizando la API de OpenWeatherMap.
    
    :param city_name: Nombre de la ciudad para la cual se desea obtener el clima.
    :return: Una cadena con la temperatura y descripción del clima, o un mensaje de error si la ciudad no se encuentra.
    """
    complete_url = BASE_URL + 'q=' + city_name + "&appid=" + API_KEY
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] != "404":
        main_data = data["main"]
        weather_data = data["weather"][0]
        temperature = main_data["temp"] - 273.15  # Convertir de Kelvin a Celsius
        description = weather_data["description"]
        return f"Temperatura: {temperature:.2f}ºC\nDescripción: {description}\nClima: {weather_data['main']}"
    else:
        return 'Ciudad no encontrada'

@bot.message_handler(commands=['clima'])
def send_weather(message):
    city_name = message.text.split()[1] if len(message.text.split()) > 1 else None
    if city_name:
        weather_info = get_weather(city_name)
        bot.reply_to(message, weather_info)
    else:
        bot.reply_to(message, 'Ciudad no encontrada, tiene que ser así: /clima Madrid')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Hola, soy un bot de prueba muy simple')

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, 'Para interactuar conmigo usa el comando start')

@bot.message_handler(commands=['pizza'])
def send_options(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_si = types.InlineKeyboardButton('Si', callback_data='pizza_si')
    btn_no = types.InlineKeyboardButton('No', callback_data='pizza_no')
    markup.add(btn_si, btn_no) 
    bot.send_message(message.chat.id, "¿Te gusta la pizza?", reply_markup=markup)

@bot.message_handler(commands=['foto'])
def send_image(message):
    img_url = 'https://esports.as.com/2020/01/07/Vegetta.png?hash=619afe072e4d1934a50f2e7fd1c0911b51a74e2c'
    bot.send_photo(chat_id=message.chat.id, photo=img_url, caption='Eh Vegetta')

@bot.message_handler(commands=['foto2'])
def another_photo(message):
    img_2 = 'https://esports.as.com/2020/01/08/sTaXx.png?hash=30d548b4776f5ecf870b5b3df82bac1b9a16c92d'
    bot.send_photo(chat_id=message.chat.id, photo=img_2, caption='Este es mi chinito willyrex')

@bot.message_handler(commands=['eleccion'])
def send_options_eleccion(message):
    markup = types.InlineKeyboardMarkup(row_width=3)  # Definimos 3 botones por fila
    btn_vegeta = types.InlineKeyboardButton('Vegetta', callback_data='vegeta')
    btn_willy = types.InlineKeyboardButton('Willy', callback_data='willy')
    btn_stax = types.InlineKeyboardButton('Staxx', callback_data='staxx')
    markup.add(btn_vegeta, btn_willy, btn_stax)
    bot.send_message(message.chat.id, "Elige a tu favorito", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    # Manejo de respuestas para el comando /pizza
    if call.data in ['pizza_si', 'pizza_no']:
        if call.data == 'pizza_si':
            bot.answer_callback_query(call.id, '¡A mí también!')
        elif call.data == 'pizza_no':
            bot.answer_callback_query(call.id, 'Qué pena, a mí sí me gusta mucho')
    # Manejo de respuestas para el comando /eleccion
    elif call.data in ['vegeta', 'willy', 'staxx']:
        # URLs de las imágenes
        img_vegeta = 'https://esports.as.com/2020/01/07/Vegetta.png?hash=619afe072e4d1934a50f2e7fd1c0911b51a74e2c'
        img_willy = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ1dPwk_NF6L526qCG7Szj30eP09-f9OFpbPg&s'
        img_staxx = 'https://esports.as.com/2020/01/08/sTaXx.png?hash=30d548b4776f5ecf870b5b3df82bac1b9a16c92d'
        if call.data == 'vegeta':
            bot.send_photo(chat_id=call.message.chat.id, photo=img_vegeta, caption='Eh Vegetta')
        elif call.data == 'willy':
            bot.send_photo(chat_id=call.message.chat.id, photo=img_willy, caption='¡Willy, tío!')
        elif call.data == 'staxx':
            bot.send_photo(chat_id=call.message.chat.id, photo=img_staxx, caption='Este es mi chinito Staxx')
        bot.answer_callback_query(call.id)

if __name__ == "__main__":
    bot.polling(none_stop=True)
