import telebot
#Conexion con el bot 
TOKEN = '7866951841:AAFhmJurjHhVNDaSsn8k80aqzLnh1saYMB8'
bot= telebot.TeleBot(TOKEN)


#Metodos

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Hola, soy un bot de prueba muy simple')
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, 'Para interactuar conmigo usa el comando start')


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message)



if __name__ == "__main__":
    bot.polling(none_stop=True)
