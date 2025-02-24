import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
# Conexión con el bot
TOKEN = '7866951841:AAFhmJurjHhVNDaSsn8k80aqzLnh1saYMB8'
bot = telebot.TeleBot(TOKEN)

conexion=sqlite3.connect("bot.db")  #Creamos la base de datos que se llama bot.db
cursor= conexion.cursor()#Creamos un cursor que es lo que ser necesita para hacer consultas, crear tablas etc   

cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios( id INTEGER PRIMARY KEY, nombre TEXT)
               --Creas una tabla que se llama usuariosy le añades la columna id que es la primria y es un integer y la nombre que es tipo texto
  
               """)

cursor.execute("INSERT INTO usuarios(id, nombre) VALUES (?,?)",(0,"Juan"))


conexion.commit()

print("BAse de datos y columnas creadas con éxito, y datos añadidos")