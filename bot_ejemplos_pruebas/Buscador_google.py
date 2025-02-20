import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from duckduckgo_search import DDGS  # Librería para buscar en DuckDuckGo

# Conexión con el bot
TOKEN = '7866951841:AAFhmJurjHhVNDaSsn8k80aqzLnh1saYMB8'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['botones'])
def cmd_botones(message):
    markup = InlineKeyboardMarkup(row_width=2)
    b1 = InlineKeyboardButton("Wikiloc", url="https://es.wikiloc.com/")
    b2 = InlineKeyboardButton("AllTrails", url="https://www.alltrails.com/es/?ref=header")
    b3 = InlineKeyboardButton("Misenda", url="https://misendafedme.es/")
    b4 = InlineKeyboardButton("Web turismo", url="https://www.andalucia.org/es/inicio")
    b5 = InlineKeyboardButton("Agencia meteorológica", url="https://www.aemet.es/es/portada")
    markup.add(b1, b2, b3, b4, b5)
    bot.send_message(message.chat.id, "Elija lo que desea mirar", reply_markup=markup)

@bot.message_handler(commands=['buscar'])
def cdm_buscar(message):
    texto_buscar = " ".join(message.text.split()[1:])
    
    if not texto_buscar:
        texto = 'Debes introducir una búsqueda. \n'
        texto += 'Ejemplo:\n'
        texto += f'<code>{message.text} friki</code>'
        bot.send_message(message.chat.id, texto, parse_mode="html")
        return

    print(f'Buscando en DuckDuckGo: "{texto_buscar}"')

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(texto_buscar, region="es-es", max_results=5))  # 5 resultados en español

        if not results:
            bot.send_message(message.chat.id, "No se encontraron resultados.")
            return

        # Enviar los resultados al usuario
        mensaje = "🔎 *Resultados de la búsqueda:*\n\n"
        for result in results:
            titulo = result.get("title", "Sin título")
            url = result.get("href", "#")
            mensaje += f"🔹 [{titulo}]({url})\n"

        bot.send_message(message.chat.id, mensaje, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        print(f"Error al buscar: {e}")
        bot.send_message(message.chat.id, "Hubo un error al procesar la búsqueda.")

if __name__ == "__main__":
    print("BOT INICIADO")
    bot.polling(none_stop=True)
