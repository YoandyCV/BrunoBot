import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os

TOKEN = os.getenv('TOKEN', '')

# Cargar la lista de APKs desde un archivo JSON
def cargar_apks():
    try:
        with open('apks.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Guardar la lista de APKs en un archivo JSON
def guardar_apks(apk_files):
    with open('apks.json', 'w') as file:
        json.dump(apk_files, file)

# Lista para almacenar los archivos APK
apk_files = cargar_apks()

# Comando /lista para mostrar los APK registrados
async def lista(update: Update, context: CallbackContext):
    if apk_files:
        message = "Lista de APKs subidos al grupo:\n\n" + "\n".join(apk_files)
    else:
        message = "No se han registrado archivos APK en el grupo."
    await update.message.reply_text(message)

# Comando /nota para anclar un texto en el chat
async def nota(update: Update, context: CallbackContext):
    texto = ' '.join(context.args)
    if texto:
        await update.message.reply_text(f"Nota anclada: {texto}")
        await context.bot.pin_chat_message(update.message.chat_id, update.message.message_id)
    else:
        await update.message.reply_text("Por favor, proporciona un texto para anclar. Ejemplo: /nota Este es un recordatorio importante.")

# Comando /ayuda para mostrar los comandos disponibles
async def ayuda(update: Update, context: CallbackContext):
    comandos = [
        "/lista - Muestra la lista de APKs subidos al grupo.",
        "/nota [texto] - Ancla un texto en el chat.",
        "/agregar [nombre_apk] - Añade un APK a la lista sin subir el archivo.",
        "/eliminar [nombre_apk] - Elimina un APK de la lista.",
        "/ayuda - Muestra esta lista de comandos."
    ]
    await update.message.reply_text("Comandos disponibles:\n\n" + "\n".join(comandos))

# Comando /agregar para añadir un APK a la lista sin subir el archivo
async def agregar(update: Update, context: CallbackContext):
    nombre_apk = ' '.join(context.args)
    if nombre_apk:
        if nombre_apk not in apk_files:
            apk_files.append(nombre_apk)
            guardar_apks(apk_files)  # Guarda la lista actualizada en el archivo JSON
            await update.message.reply_text(f"APK '{nombre_apk}' añadido a la lista.")
        else:
            await update.message.reply_text(f"El APK '{nombre_apk}' ya está en la lista.")
    else:
        await update.message.reply_text("Por favor, proporciona el nombre del APK. Ejemplo: /agregar nombre_del_apk.apk")

# Comando /eliminar para eliminar un APK de la lista
async def eliminar(update: Update, context: CallbackContext):
    nombre_apk = ' '.join(context.args)
    if nombre_apk:
        if nombre_apk in apk_files:
            apk_files.remove(nombre_apk)
            guardar_apks(apk_files)  # Guarda la lista actualizada en el archivo JSON
            await update.message.reply_text(f"APK '{nombre_apk}' eliminado de la lista.")
        else:
            await update.message.reply_text(f"El APK '{nombre_apk}' no está en la lista.")
    else:
        await update.message.reply_text("Por favor, proporciona el nombre del APK. Ejemplo: /eliminar nombre_del_apk.apk")

# Handler para detectar archivos APK subidos
async def detect_apk(update: Update, context: CallbackContext):
    if update.message.document:  # Verifica si el mensaje contiene un archivo
        document = update.message.document
        if document.mime_type == "application/vnd.android.package-archive":  # Verifica si es un APK
            file_name = document.file_name
            if file_name not in apk_files:
                apk_files.append(file_name)  # Guarda el nombre del archivo en la lista
                guardar_apks(apk_files)  # Guarda la lista actualizada en el archivo JSON
                await update.message.reply_text(f"Archivo APK detectado: {file_name} guardado en la lista.")
            else:
                await update.message.reply_text(f"El APK '{file_name}' ya está en la lista.")

# Configuración del bot
def main():
    
    # Crea la aplicación y pasa el token
    application = Application.builder().token(TOKEN).build()

    # Comandos
    application.add_handler(CommandHandler("lista", lista))
    application.add_handler(CommandHandler("nota", nota))
    application.add_handler(CommandHandler("agregar", agregar))
    application.add_handler(CommandHandler("eliminar", eliminar))
    application.add_handler(CommandHandler("ayuda", ayuda))

    # Detectar archivos subidos (solo APKs)
    application.add_handler(MessageHandler(filters.Document.MimeType("application/vnd.android.package-archive"), detect_apk))

    # Inicia el bot
    application.run_polling()

if __name__ == '__main__':
    print("Iniciando...")
    main()