import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! لطفا یک فایل صوتی ارسال کن تا به متن تبدیلش کنم."
    )

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = None
    if update.message.voice:
        file = await update.message.voice.get_file()
    elif update.message.audio:
        file = await update.message.audio.get_file()
    elif update.message.document:
        if update.message.document.mime_type.startswith("audio/"):
            file = await update.message.document.get_file()

    if not file:
        await update.message.reply_text("لطفا یک فایل صوتی معتبر ارسال کنید.")
        return

    file_path = await file.download_to_drive()

    await update.message.reply_text("در حال تبدیل صوت به متن... لطفا صبر کنید.")

    with open(file_path, "rb") as audio_file:
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
        text = transcription["text"]

    await update.message.reply_text(f"متن تبدیل شده:\n\n{text}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO | filters.Document.AUDIO, handle_audio))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
