import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Keys
TELEGRAM_TOKEN = "8950301339:AAEIH6GgLXWtGjCocZfRVoSimD91T-VzHvY"
GEMINI_KEY = "AQ.Ab8RN6KWT1H7iHRZOWBOgiU7KSL2TU8cDSmECkUJVzJomEpIwA"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("नमस्ते! मैं AI सपोर्ट बॉट हूँ। आप मुझसे कोई भी सवाल पूछ सकते हैं।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("माफ़ कीजिए, उत्तर देने में समस्या आई।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is starting...")
    app.run_polling()
  
