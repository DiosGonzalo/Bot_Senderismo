import os
import random
import string
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from telegram.ext import ContextTypes
from cryptography.fernet import Fernet

# Token de Telegram (¡REEMPLAZA ESTO CON TU TOKEN REAL DE BOTFATHER!)
TOKEN = "7741007189:AAHfPIhltYVu22WmdubIBjXXknI_2u9lgs0"

# Estados para la conversación
PIN, OPTION, SAVE_PASSWORD, VIEW_PASSWORD, GENERATE_PASSWORD = range(5)

# Database setup
DB_FILE = "passwords.db"
KEY_FILE = "secret.key"

# Generar clave de cifrado si no existe
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
with open(KEY_FILE, "rb") as key_file:
    CIPHER = Fernet(key_file.read())

# Inicializar base de datos SQLite
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id TEXT PRIMARY KEY, pin TEXT, paid INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS passwords 
                 (user_id TEXT, site TEXT, password TEXT, 
                 FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    conn.commit()
    conn.close()

# Función para mostrar el menú
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, message="¿Qué desea hacer?"):
    keyboard = [
        [InlineKeyboardButton("Guardar contraseña", callback_data="save")],
        [InlineKeyboardButton("Ver contraseñas", callback_data="view")],
        [InlineKeyboardButton("Generar contraseña", callback_data="generate")],
        [InlineKeyboardButton("Info", callback_data="info")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("SELECT pin FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()

    if not result:
        await update.message.reply_text("Bienvenido. Establece un PIN de 4 dígitos para proteger tus contraseñas:")
        return PIN
    else:
        await show_menu(update, context, message="Bienvenido de nuevo. ¿Qué desea hacer?")
        return OPTION

# Comando /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("SELECT pin FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()

    if not result:
        await update.message.reply_text("Primero configura un PIN con /start.")
        return ConversationHandler.END
    else:
        await show_menu(update, context)
        return OPTION

# Establecer PIN
async def set_pin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    pin = update.message.text

    if not pin.isdigit() or len(pin) != 4:
        await update.message.reply_text("Por favor, introduce un PIN de 4 dígitos.")
        return PIN

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, pin) VALUES (?, ?)", (user_id, pin))
    conn.commit()
    conn.close()

    await update.message.reply_text("PIN establecido correctamente.")
    await show_menu(update, context)
    return ConversationHandler.END

# Manejar opciones del menú
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    option = query.data

    if option == "save":
        await query.edit_message_text("Envíame la contraseña que quieres guardar (ejemplo: 'sitio:contraseña'):")
        return SAVE_PASSWORD
    elif option == "view":
        await query.edit_message_text("Introduce tu PIN para ver tus contraseñas:")
        return VIEW_PASSWORD
    elif option == "generate":
        await query.edit_message_text("¿Cuántos caracteres quieres que tenga la contraseña? (8-32)")
        return GENERATE_PASSWORD
    elif option == "info":
        info_text = (
            "💡 *Comandos y cómo funciona:*\n"
            "- *Guardar contraseña*: Usa 'sitio:contraseña' para guardar una contraseña.\n"
            "- *Ver contraseñas*: Introduce tu PIN para ver todas tus contraseñas.\n"
            "- *Generar contraseña*: Elige la longitud y obtén una contraseña segura.\n"
            "- Usa /menu en cualquier momento para ver las opciones.\n\n"
            "🔒 *Seguridad*: Tus contraseñas se guardan cifradas con una clave única.\n\n"
            "💸 *Nota*: Actualmente el límite de 15 contraseñas está desactivado."
        )
        await query.edit_message_text(info_text)
        await show_menu(update, context)
        return OPTION

# Guardar contraseña
async def save_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    text = update.message.text

    if ":" not in text:
        await update.message.reply_text("Formato incorrecto. Usa 'sitio:contraseña'.")
        return SAVE_PASSWORD

    site, password = text.split(":", 1)
    encrypted_password = CIPHER.encrypt(password.encode()).decode()

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO passwords (user_id, site, password) VALUES (?, ?, ?)", 
             (user_id, site, encrypted_password))
    conn.commit()
    conn.close()
    
    await update.message.reply_text(f"Contraseña guardada para '{site}'.")
    # Enviar un nuevo mensaje con el menú en lugar de editar el anterior
    await update.message.reply_text("¿Qué desea hacer?", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Guardar contraseña", callback_data="save")],
        [InlineKeyboardButton("Ver contraseñas", callback_data="view")],
        [InlineKeyboardButton("Generar contraseña", callback_data="generate")],
        [InlineKeyboardButton("Info", callback_data="info")],
    ]))
    return ConversationHandler.END

# Ver contraseñas
async def view_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    pin = update.message.text
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("SELECT pin FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    if not result:
        await update.message.reply_text("No tienes un PIN configurado. Usa /start para configurarlo.")
        conn.close()
        return ConversationHandler.END
    stored_pin = result[0]
    
    if pin != stored_pin:
        await update.message.reply_text("PIN incorrecto.")
        conn.close()
        return ConversationHandler.END

    c.execute("SELECT site, password FROM passwords WHERE user_id = ?", (user_id,))
    passwords = c.fetchall()
    conn.close()

    if not passwords:
        await update.message.reply_text("No tienes contraseñas guardadas.")
    else:
        response = "Tus contraseñas:\n"
        for site, enc_pwd in passwords:
            pwd = CIPHER.decrypt(enc_pwd.encode()).decode()
            response += f"{site}: {pwd}\n"
        await update.message.reply_text(response)
    
    # Enviar un nuevo mensaje con el menú
    await update.message.reply_text("¿Qué desea hacer?", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Guardar contraseña", callback_data="save")],
        [InlineKeyboardButton("Ver contraseñas", callback_data="view")],
        [InlineKeyboardButton("Generar contraseña", callback_data="generate")],
        [InlineKeyboardButton("Info", callback_data="info")],
    ]))
    return ConversationHandler.END

# Generar contraseña
async def generate_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        length = int(update.message.text)
        if length < 8 or length > 32:
            await update.message.reply_text("Elige entre 8 y 32 caracteres.")
            return GENERATE_PASSWORD
    except ValueError:
        await update.message.reply_text("Por favor, introduce un número.")
        return GENERATE_PASSWORD

    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    await update.message.reply_text(f"Tu nueva contraseña: {password}")
    
    # Enviar un nuevo mensaje con el menú
    await update.message.reply_text("¿Qué desea hacer?", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Guardar contraseña", callback_data="save")],
        [InlineKeyboardButton("Ver contraseñas", callback_data="view")],
        [InlineKeyboardButton("Generar contraseña", callback_data="generate")],
        [InlineKeyboardButton("Info", callback_data="info")],
    ]))
    return ConversationHandler.END

# Main
def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("menu", menu)],
        states={
            PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_pin)],
            OPTION: [CallbackQueryHandler(button)],
            SAVE_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_password)],
            VIEW_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, view_password)],
            GENERATE_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_password)],
        },
        fallbacks=[],
        per_message=False
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()