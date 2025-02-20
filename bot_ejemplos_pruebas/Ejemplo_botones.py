import telebot
from telebot.types import ReplyKeyboardMarkup, ForceReply

TOKEN = '7866951841:AAFhmJurjHhVNDaSsn8k80aqzLnh1saYMB8'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def cm_start(message):
    bot.send_message(message.chat.id, "Usa el comando /alta para introducir tus datos")

@bot.message_handler(commands=['alta'])
def cmd_alta(message):
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿Cuál es tu nombre?", reply_markup=markup)
    bot.register_next_step_handler(msg, preguntar_edad)

def preguntar_edad(message):
    nombre = message.text  # Guardamos el nombre
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿Cuántos años tienes?", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: validar_edad(m, nombre))  # Pasamos el nombre

def validar_edad(message, nombre):
    if not message.text.isdigit():
        msg = bot.send_message(message.chat.id, "Debes introducir un número.\nDiga su edad:")
        bot.register_next_step_handler(msg, lambda m: validar_edad(m, nombre))
    else:
        edad = message.text  # Guardamos la edad
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder="Pulsa un botón")
        markup.add("Hombre", "Mujer")
        msg = bot.send_message(message.chat.id, "¿Cuál es tu sexo?", reply_markup=markup)
        bot.register_next_step_handler(msg, lambda m: confirmar_datos(m, nombre, edad))  # Pasamos nombre y edad

def confirmar_datos(message, nombre, edad):
    sexo = message.text  # Guardamos el sexo
    bot.send_message(message.chat.id, f"Datos guardados:\nNombre: {nombre}\nEdad: {edad}\nSexo: {sexo}")

if __name__ == "__main__":
    print("INICIANDO BOT")
    bot.polling(none_stop=True)
