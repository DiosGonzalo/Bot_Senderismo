import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
# Conexión con el bot
TOKEN = '7866951841:AAFhmJurjHhVNDaSsn8k80aqzLnh1saYMB8'
bot = telebot.TeleBot(TOKEN)

conexion=sqlite3.connect("bot.db")  #Creamos la base de datos que se llama bot.db
cursor= conexion.cursor()#Creamos un cursor que es lo que ser necesita para hacer consultas, crear tablas etc   

# Crear la tabla sin AUTOINCREMENT para permitir ID manual
cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY, 
        nombre TEXT
    )
""")
    conexion.commit()
    conexion.close()


# Métodos

# Función para guardar un usuario en la base de datos
def guardar_usuario(user_id, nombre):
    conexion = sqlite3.connect("bot.db")
    cursor = conexion.cursor()
    cursor.execute("INSERT OR IGNORE INTO usuarios (id, nombre) VALUES (?, ?)", (user_id, nombre))
    conexion.commit()
    conexion.close()

# Comando /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    nombre = message.from_user.first_name

    guardar_usuario(user_id, nombre)
    bot.reply_to(message, f"¡Hola {nombre}! Te he guardado en la base de datos. 😊")

# Iniciar el bot
if __name__ == "__main__":
    conectar_bd()  # Crear la base de datos si no existe
    print("Bot iniciado...")
    bot.infinity_polling()