"""Key changes and fixes:

Fixed NameError: Replaced CallbackContext with ContextTypes.DEFAULT_TYPE and added async to all handler functions to match the latest python-telegram-bot API (v20+).
SQLite3 Database: Replaced JSON storage with SQLite3, creating two tables:
users: Stores user_id, pin, and paid status
passwords: Stores encrypted passwords linked to users
PayPal Integration:
Added paypalrestsdk for real payment processing
Implemented /pay command that creates a PayPal payment
Added /verify command to confirm payment completion
You'll need to:
Install paypalrestsdk (pip install paypalrestsdk)
Get PayPal API credentials (client_id and client_secret) from PayPal Developer
Set up proper return URLs (replace the localhost URLs)
Change "sandbox" to "live" for production
Additional Requirements:
Replace "YOUR_TELEGRAM_TOKEN" with your BotFather token
Replace "YOUR_PAYPAL_CLIENT_ID" and "YOUR_PAYPAL_CLIENT_SECRET" with your PayPal credentials
To use this:

Install required packages:
bash
Ajuste
Copiar
pip install python-telegram-bot cryptography paypalrestsdk sqlite3
Set up your PayPal developer account and get API credentials
Update the token and PayPal credentials in the code
Set up a webhook or local server for payment verification URLs
Run the script
The bot now uses a proper database and real PayPal payments instead of simulated ones. Users will need
 to complete the payment through PayPal and then use /verify to confirm their payment status."""

import json
import os
import random
import string
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from telegram.ext import ContextTypes  # Replaced CallbackContext with ContextTypes
from cryptography.fernet import Fernet
import paypalrestsdk

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": "YOUR_PAYPAL_CLIENT_ID",
    "client_secret": "YOUR_PAYPAL_CLIENT_SECRET"
})

# Estados para la conversación
PIN, OPTION, SAVE_PASSWORD, VIEW_PASSWORD, GENERATE_PASSWORD = range(5)

# Database setup
DB_FILE = "passwords.db"
KEY_FILE = "secret.key"

# Generate encryption key if it doesn't exist
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
with open(KEY_FILE, "rb") as key_file:
    CIPHER = Fernet(key_file.read())

# Initialize SQLite database
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

# Menú principal
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("SELECT pin FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    
    if not result:
        await update.message.reply_text("Primero, establece un PIN de 4 dígitos para proteger tus contraseñas:")
        conn.close()
        return PIN

    keyboard = [
        [InlineKeyboardButton("Guardar contraseña", callback_data="save")],
        [InlineKeyboardButton("Ver contraseñas", callback_data="view")],
        [InlineKeyboardButton("Generar contraseña", callback_data="generate")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("¿Qué desea hacer?", reply_markup=reply_markup)
    conn.close()
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

    await update.message.reply_text("PIN establecido correctamente. Usa /start para comenzar.")
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
    
    c.execute("SELECT paid FROM users WHERE user_id = ?", (user_id,))
    paid = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM passwords WHERE user_id = ?", (user_id,))
    count = c.fetchone()[0]

    if count >= 15 and not paid:
        await update.message.reply_text("Has alcanzado el límite de 15 contraseñas. Paga 5€ (usa /pay) para almacenar más.")
        conn.close()
        return ConversationHandler.END

    c.execute("INSERT INTO passwords (user_id, site, password) VALUES (?, ?, ?)", 
             (user_id, site, encrypted_password))
    conn.commit()
    conn.close()
    
    await update.message.reply_text(f"Contraseña guardada para '{site}'.")
    return ConversationHandler.END

# Ver contraseñas
async def view_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    pin = update.message.text
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("SELECT pin FROM users WHERE user_id = ?", (user_id,))
    stored_pin = c.fetchone()[0]
    
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
    return ConversationHandler.END

# Pago con PayPal
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "transactions": [{
            "amount": {
                "total": "5.00",
                "currency": "EUR"
            },
            "description": "Acceso ilimitado al bot de contraseñas"
        }],
        "redirect_urls": {
            "return_url": "http://localhost:8000/success",  # Change this to your success URL
            "cancel_url": "http://localhost:8000/cancel"    # Change this to your cancel URL
        }
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                await update.message.reply_text(f"Por favor, completa el pago aquí: {link.href}")
                context.user_data['payment_id'] = payment.id
    else:
        await update.message.reply_text("Error al crear el pago. Intenta de nuevo.")

# Verificar pago
async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    payment_id = context.user_data.get('payment_id')
    
    if not payment_id:
        await update.message.reply_text("No hay pago pendiente.")
        return

    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payment.payer.payer_info.payer_id}):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE users SET paid = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        await update.message.reply_text("Pago recibido (5€). Ahora puedes guardar contraseñas ilimitadas.")
    else:
        await update.message.reply_text("Error al verificar el pago.")

# Main
def main():
    init_db()
    application = Application.builder().token("7741007189:AAHfPIhltYVu22WmdubIBjXXknI_2u9lgs0").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_pin)],
            OPTION: [CallbackQueryHandler(button)],
            SAVE_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_password)],
            VIEW_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, view_password)],
            GENERATE_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_password)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("pay", pay))
    application.add_handler(CommandHandler("verify", verify_payment))

    application.run_polling()

if __name__ == "__main__":
    main()