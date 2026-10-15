import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Render को 24/7 एक्टिव रखने के लिए बैकग्राउंड पोर्ट सर्वर
class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run():
    server = HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), SimpleServer)
    server.serve_forever()

threading.Thread(target=run, daemon=True).start()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = "8950301339:AAHhaMne1-kVQN26vLlS07QKoUMnF4J2-yo"

SYSTEM_INSTRUCTION = """
आप MD Istiak Trader Support के आधिकारिक VIP ट्रेडिंग सपोर्टर और मुख्य रिस्क मैनेजर असिस्टेंट हैं।
अगर यूजर की भाषा 'hi' है तो शुद्ध, अनुशासित, व्यावहारिक और आदरणीय सीनियर ट्रेडर भाई की तरह देसी हिंदी में बात करें।
अगर यूजर की भाषा 'en' है तो clear, professional English में बात करें।

28 VIP टियर्स मैट्रिक्स (L1 / L2 / L3 लॉट):
VIP 1 ($100-249|5%): Gold: -/0.01/- | Oil: 0.01/0.01/- | Silver: -/0.01/- | BTC: 0.01/0.01/- | ETH: 0.09/0.15/0.05
VIP 2 ($250-499|5%): Gold: -/0.01/0.01 | Oil: -/0.02/0.01 | Silver: -/0.01/0.01 | BTC: 0.01/0.02/0.01 | ETH: 0.22/0.37/0.15
VIP 3 ($500-750|5%): Gold: 0.01/0.01/0.01 | Oil: 0.02/0.02/0.02 | Silver: 0.01/0.01/0.01 | BTC: 0.02/0.03/0.01 | ETH: 0.44/0.73/0.30
VIP 4 ($750-1200|4%): Gold: 0.01/0.01/0.02 | Oil: 0.02/0.02/0.04 | Silver: 0.01/0.01/0.01 | BTC: 0.02/0.05/0.02 | ETH: 0.53/0.88/0.35
VIP 5 ($1200-1700|3.5%): Gold: 0.01/0.02/0.03 | Oil: 0.02/0.04/0.06 | Silver: 0.01/0.02/0.01 | BTC: 0.03/0.06/0.02 | ETH: 0.74/1.23/0.49
VIP 6 ($1700-2200|3%): Gold: 0.02/0.02/0.03 | Oil: 0.04/0.04/0.06 | Silver: 0.01/0.02/0.01 | BTC: 0.04/0.07/0.02 | ETH: 0.90/1.50/0.59
VIP 7 ($2200-2600|3%): Gold: 0.02/0.03/0.03 | Oil: 0.04/0.06/0.06 | Silver: 0.01/0.02/0.01 | BTC: 0.05/0.09/0.03 | ETH: 1.16/1.94/0.77
VIP 8 ($2600-3000|3%): Gold: 0.02/0.03/0.04 | Oil: 0.04/0.06/0.08 | Silver: 0.01/0.03/0.01 | BTC: 0.06/0.11/0.03 | ETH: 1.37/2.29/0.91
VIP 9 ($3000-3500|2.5%): Gold: 0.03/0.03/0.04 | Oil: 0.06/0.06/0.08 | Silver: 0.01/0.03/0.01 | BTC: 0.06/0.10/0.05 | ETH: 1.45/2.42/0.96
VIP 10 ($3500-4000|2.5%): Gold: 0.03/0.04/0.04 | Oil: 0.06/0.08/0.08 | Silver: 0.01/0.03/0.02 | BTC: 0.06/0.10/0.05 | ETH: 1.55/2.58/1.03
VIP 11 ($4000-4500|2%): Gold: 0.03/0.05/0.04 | Oil: 0.06/0.10/0.08 | Silver: 0.01/0.03/0.01 | BTC: 0.06/0.11/0.03 | ETH: 1.60/2.66/1.06
VIP 12 ($4500-5000|2%): Gold: 0.03/0.06/0.03 | Oil: 0.06/0.12/0.06 | Silver: 0.01/0.03/0.02 | BTC: 0.07/0.11/0.04 | ETH: 1.65/2.75/1.10
VIP 13 ($5000-5500|2%): Gold: 0.03/0.07/0.04 | Oil: 0.06/0.14/0.08 | Silver: 0.01/0.04/0.01 | BTC: 0.07/0.12/0.05 | ETH: 1.76/2.94/1.17
VIP 14 ($5500-6000|2%): Gold: 0.04/0.07/0.04 | Oil: 0.08/0.14/0.08 | Silver: 0.01/0.04/0.02 | BTC: 0.08/0.14/0.05 | ETH: 1.94/3.23/1.29
VIP 15 ($6000-7000|2%): Gold: 0.04/0.08/0.04 | Oil: 0.08/0.16/0.08 | Silver: 0.01/0.05/0.02 | BTC: 0.09/0.14/0.06 | ETH: 2.12/3.53/1.41
VIP 16 ($7000-8000|2%): Gold: 0.04/0.09/0.04 | Oil: 0.08/0.18/0.08 | Silver: 0.01/0.06/0.02 | BTC: 0.10/0.17/0.07 | ETH: 2.47/4.12/1.65
VIP 17 ($8000-10000|2%): Gold: 0.04/0.10/0.04 | Oil: 0.08/0.20/0.08 | Silver: 0.01/0.07/0.02 | BTC: 0.12/0.20/0.07 | ETH: 2.82/4.71/1.88
VIP 18 ($10000-15000|2%): Gold: 0.05/0.11/0.04 | Oil: 0.10/0.22/0.08 | Silver: 0.02/0.08/0.02 | BTC: 0.15/0.24/0.10 | ETH: 3.53/5.88/2.35
VIP 19 ($15000-25000|2%): Gold: 0.06/0.13/0.04 | Oil: 0.12/0.26/0.08 | Silver: 0.02/0.13/0.03 | BTC: 0.22/0.36/0.15 | ETH: 5.29/8.82/3.53
VIP 20 ($25000-35000|2%): Gold: 0.06/0.15/0.05 | Oil: 0.12/0.30/0.10 | Silver: 0.03/0.22/0.05 | BTC: 0.37/0.61/0.24 | ETH: 8.82/14.70/5.88
VIP 21 ($35k-50k|2%), VIP 22 ($50k-75k|2%), VIP 23 ($75k-100k|2%), VIP 24 ($100k-150k|1.5%), VIP 25 ($150k-200k|1.5%), VIP 26 ($200k-300k|1.25%), VIP 27 ($300k-500k|1%), VIP 28 ($500k-1M|1%).

बातचीत के मुख्य नियम:
1. यूज़र बैलेंस बताए: VIP टियर, फिक्स्ड रिस्क % और डॉलर रिस्क बजट बताएं। फिर पूछें कि कौन से पेयर (Gold, Oil, Silver, BTC, ETH) पर ट्रेड करना चाहते हैं।
2. यूज़र पेयर बताए: L1 (31%), L2 (48%), L3 (65%) के सटीक लॉट, कुल लॉट और VIP अपग्रेड की तुलना दें।
3. कोई सवाल पूछे: बिना रूल नंबर बोले सीधा सटीक और पक्का टेक्निकल समाधान दें।
"""

def ask_gemini(messages_history: list) -> str:
    key = os.environ.get("GEMINI_KEY", "").strip()
    if not key:
        return "Error: API key is not set in Environment."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": messages_history,
        "temperature": 0.3,
        "max_tokens": 1024
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        data = response.json()
        if response.status_code == 200:
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error: {data.get('error', {}).get('message', str(data))}"
    except Exception as e:
        return f"Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # यूज़र की पुरानी हिस्ट्री और भाषा रीसेट करना
    context.user_data["history"] = []
    context.user_data["lang"] = "hi"

    keyboard = [
        [
            InlineKeyboardButton("🇮🇳 हिन्दी (Hindi)", callback_data="lang_hi"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "नमस्ते / Welcome to **MD Istiak Trader Support**!\n\n"
        "कृपया अपनी पसंदीदा भाषा चुनें / Please select your preferred language:"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "lang_hi":
        context.user_data["lang"] = "hi"
        msg = (
            "नमस्ते भाई! मैं **Gold Master Multi-Asset EA** का आधिकारिक सपोर्टर हूँ। 🙏\n\n"
            "कृपया अपना **खाता बैलेंस (USD में)** बताइए, ताकि मैं आपका सही VIP टियर, रिस्क बजट और लॉट साइज़ निकाल सकूँ।"
        )
    else:
        context.user_data["lang"] = "en"
        msg = (
            "Welcome! I am the official **Gold Master Multi-Asset EA** support assistant. 🤝\n\n"
            "Please share your **account balance (in USD)** so I can determine your exact VIP tier, risk budget, and lot sizes."
        )

    await query.edit_message_text(msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_lang = context.user_data.get("lang", "hi")

    # चैट हिस्ट्री निकालना ताकि पिछली बातें याद रहें
    history = context.user_data.get("history", [])

    current_system_prompt = f"{SYSTEM_INSTRUCTION}\nयूजर की चुनी गई भाषा: '{user_lang}'"
    messages = [{"role": "system", "content": current_system_prompt}]

    # पुरानी बातचीत जोड़ना
    for h in history:
        messages.append(h)

    # नया संदेश जोड़ना
    messages.append({"role": "user", "content": user_text})

    # AI से जवाब लेना
    bot_reply = ask_gemini(messages)

    # मेमोरी में चैट सेव रखना (पिछली 6 बातचीत याद रखेगा)
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": bot_reply})
    if len(history) > 6:
        history = history[-6:]
    context.user_data["history"] = history

    await update.message.reply_text(bot_reply)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is starting...")
    app.run_polling()
