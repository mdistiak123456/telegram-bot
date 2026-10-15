import os
import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Render Environment Variables (पुराने नाम बिल्कुल वैसे ही रखे हैं)
API_KEY = os.environ.get("GEMINI_KEY", "").strip()
MODEL_NAME = "openai/gpt-oss-120b"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# 28-Level VIP Matrix Reference
VIP_MATRIX = """
VIP 1 ($100–$249 | 5% | ~$5-$12.5): Gold: —/0.01/— | Oil: 0.01/0.01/— | Silver: —/0.01/— | BTC: 0.01/0.01/— | ETH: 0.09/0.15/0.05
VIP 2 ($250–$499 | 5% | $12.5-$25): Gold: —/0.01/0.01 | Oil: —/0.02/0.01 | Silver: —/0.01/0.01 | BTC: 0.01/0.02/0.01 | ETH: 0.22/0.37/0.15
VIP 3 ($500–$750 | 5% | $25-$37.5): Gold: 0.01/0.01/0.01 | Oil: 0.02/0.02/0.02 | Silver: 0.01/0.01/0.01 | BTC: 0.02/0.03/0.01 | ETH: 0.44/0.73/0.30
VIP 4 ($750–$1,200 | 4% | $30-$48): Gold: 0.01/0.01/0.02 | Oil: 0.02/0.02/0.04 | Silver: 0.01/0.01/0.01 | BTC: 0.02/0.05/0.02 | ETH: 0.53/0.88/0.35
VIP 5 ($1,200–$1,700 | 3.5% | $42-$59.5): Gold: 0.01/0.02/0.03 | Oil: 0.02/0.04/0.06 | Silver: 0.01/0.02/0.01 | BTC: 0.03/0.06/0.02 | ETH: 0.74/1.23/0.49
VIP 6 ($1,700–$2,200 | 3% | $51-$66): Gold: 0.02/0.02/0.03 | Oil: 0.04/0.04/0.06 | Silver: 0.01/0.02/0.01 | BTC: 0.04/0.07/0.02 | ETH: 0.90/1.50/0.59
VIP 7 ($2,200–$2,600 | 3% | $66-$78): Gold: 0.02/0.03/0.03 | Oil: 0.04/0.06/0.06 | Silver: 0.01/0.02/0.01 | BTC: 0.05/0.09/0.03 | ETH: 1.16/1.94/0.77
VIP 8 ($2,600–$3,000 | 3% | $78-$90): Gold: 0.02/0.03/0.04 | Oil: 0.04/0.06/0.08 | Silver: 0.01/0.03/0.01 | BTC: 0.06/0.11/0.03 | ETH: 1.37/2.29/0.91
VIP 9 ($3,000–$3,500 | 2.5% | $75-$87.5): Gold: 0.03/0.03/0.04 | Oil: 0.06/0.06/0.08 | Silver: 0.01/0.03/0.01 | BTC: 0.06/0.10/0.05 | ETH: 1.45/2.42/0.96
VIP 10 ($3,500–$4,000 | 2.5% | $87.5-$100): Gold: 0.03/0.04/0.04 | Oil: 0.06/0.08/0.08 | Silver: 0.01/0.03/0.02 | BTC: 0.06/0.10/0.05 | ETH: 1.55/2.58/1.03
VIP 11 ($4,000–$4,500 | 2% | $80-$90): Gold: 0.03/0.05/0.04 | Oil: 0.06/0.10/0.08 | Silver: 0.01/0.03/0.01 | BTC: 0.06/0.11/0.03 | ETH: 1.60/2.66/1.06
VIP 12 ($4,500–$5,000 | 2% | $90-$100): Gold: 0.03/0.06/0.03 | Oil: 0.06/0.12/0.06 | Silver: 0.01/0.03/0.02 | BTC: 0.07/0.11/0.04 | ETH: 1.65/2.75/1.10
VIP 13 ($5,000–$5,500 | 2% | $100-$110): Gold: 0.03/0.07/0.04 | Oil: 0.06/0.14/0.08 | Silver: 0.01/0.04/0.01 | BTC: 0.07/0.12/0.05 | ETH: 1.76/2.94/1.17
VIP 14 ($5,500–$6,000 | 2% | $110-$120): Gold: 0.04/0.07/0.04 | Oil: 0.08/0.14/0.08 | Silver: 0.01/0.04/0.02 | BTC: 0.08/0.14/0.05 | ETH: 1.94/3.23/1.29
VIP 15 ($6,000–$7,000 | 2% | $120-$140): Gold: 0.04/0.08/0.04 | Oil: 0.08/0.16/0.08 | Silver: 0.01/0.05/0.02 | BTC: 0.09/0.14/0.06 | ETH: 2.12/3.53/1.41
VIP 16 ($7,000–$8,000 | 2% | $140-$160): Gold: 0.04/0.09/0.04 | Oil: 0.08/0.18/0.08 | Silver: 0.01/0.06/0.02 | BTC: 0.10/0.17/0.07 | ETH: 2.47/4.12/1.65
VIP 17 ($8,000–$10,000 | 2% | $160-$200): Gold: 0.04/0.10/0.04 | Oil: 0.08/0.20/0.08 | Silver: 0.01/0.07/0.02 | BTC: 0.12/0.20/0.07 | ETH: 2.82/4.71/1.88
VIP 18 ($10,000–$15,000 | 2% | $200-$300): Gold: 0.05/0.11/0.04 | Oil: 0.10/0.22/0.08 | Silver: 0.02/0.08/0.02 | BTC: 0.15/0.24/0.10 | ETH: 3.53/5.88/2.35
VIP 19 ($15,000–$25,000 | 2% | $300-$500): Gold: 0.06/0.13/0.04 | Oil: 0.12/0.26/0.08 | Silver: 0.02/0.13/0.03 | BTC: 0.22/0.36/0.15 | ETH: 5.29/8.82/3.53
VIP 20 ($25,000–$35,000 | 2% | $500-$700): Gold: 0.06/0.15/0.05 | Oil: 0.12/0.30/0.10 | Silver: 0.03/0.22/0.05 | BTC: 0.37/0.61/0.24 | ETH: 8.82/14.70/5.88
VIP 21 ($35,000–$50,000 | 2% | $700-$1,000): Gold: 0.07/0.16/0.05 | Oil: 0.14/0.32/0.10 | Silver: 0.05/0.31/0.06 | BTC: 0.51/0.85/0.35 | ETH: 12.35/20.58/8.23
VIP 22 ($50,000–$75,000 | 2% | $1,000-$1,500): Gold: 0.15/0.33/0.12 | Oil: 0.30/0.66/0.24 | Silver: 0.06/0.45/0.09 | BTC: 0.73/1.22/0.49 | ETH: 17.64/29.40/11.76
VIP 23 ($75,000–$100,000 | 2% | $1,500-$2,000): Gold: 0.25/0.50/0.15 | Oil: 0.50/1.00/0.30 | Silver: 0.10/0.67/0.13 | BTC: 1.09/1.82/0.74 | ETH: 26.46/44.10/17.64
VIP 24 ($100,000–$150,000 | 1.5% | $1,500-$2,250): Gold: 0.25/0.55/0.20 | Oil: 0.50/1.10/0.40 | Silver: 0.10/0.67/0.13 | BTC: 1.09/1.82/0.74 | ETH: 26.50/44.15/17.65
VIP 25 ($150,000–$200,000 | 1.5% | $2,250-$3,000): Gold: 0.35/0.85/0.30 | Oil: 0.70/1.70/0.60 | Silver: 0.15/1.00/0.20 | BTC: 1.64/2.74/1.10 | ETH: 39.69/66.15/26.46
VIP 26 ($200,000–$300,000 | 1.25% | $2,500-$3,750): Gold: 0.50/1.00/0.30 | Oil: 1.00/2.00/0.60 | Silver: 0.16/1.12/0.22 | BTC: 1.83/3.04/1.22 | ETH: 44.10/73.50/29.40
VIP 27 ($300,000–$500,000 | 1.0% | $3,000-$5,000): Gold: 0.65/1.35/0.40 | Oil: 1.30/2.70/0.80 | Silver: 0.20/1.37/0.27 | BTC: 2.19/3.65/1.47 | ETH: 52.92/88.20/35.28
VIP 28 ($500,000–$1,000,000 | 1.0% | $5,000-$10,000): Gold: 1.00/2.20/0.60 | Oil: 2.00/4.40/1.20 | Silver: 0.32/2.26/0.44 | BTC: 3.65/6.09/2.44 | ETH: 88.20/147.00/58.80
"""

# Technical Brain (Rules & Logic without rule numbers)
KNOWLEDGE_RULES = """
- Stop Loss Hit: It is a normal part of the system. Invalidation point passed. Fixed risk budget protected 95-98% capital. Strictly NO revenge trading. Wait for next clean liquidity sweep. If 2 SL hit in a day, stop trading for the day.
- Active Cycle / Single Cycle Hard Lock: Only 1 trade cycle allowed per asset at a time. No new cycle until the previous cycle finishes.
- Hedging & Martingale: STRICTLY PROHIBITED. No double lot sizing on loss. Predetermined VIP lots only.
- Next-Bar Auto-Kill: Unfilled pending limit orders are automatically cancelled when current candle closes.
- TP & Partial Close: TP1 closes 50% volume (on >= 0.02 lots). SL moves to Break-Even immediately. 0.01 lot cannot be halved, so it runs at 100% volume to final TP. No trailing stops.
- Internet / Terminal Disconnect: Limits and SL/TP reside on broker servers, staying safe. VPS recommended for Next-Bar Auto-Kill.
- Supported Assets: XAUUSD, USOIL, XAGUSD, BTCUSD, ETHUSD on MT5. Timeframes: M15, M30, H1, H4, D1.
- State Lock Rule: Depositing or withdrawing mid-trade will not alter active lots. Upgrades apply to the next fresh cycle.
"""

user_sessions = {}

def get_system_prompt(lang: str) -> str:
    if lang == "en":
        return f"""
You are the official VIP Trading Assistant and Chief Risk Manager of 'MD Istiak Trader Support'.
Communicate in an executive, clear, professional global trading style.

{VIP_MATRIX}

{KNOWLEDGE_RULES}

RULES OF CONVERSATION:
1. Always remember the user's recorded balance. NEVER ask for balance again once recorded!
2. When the user specifies an asset (Gold, Oil, Silver, BTC, ETH), immediately output their L1 (31%), L2 (48% - core volume), L3 (65%), and Total Basket Lots.
3. Include a VIP Upgrade ROI comparison showing how adding capital moves them to the next tier for higher volume and profit with fixed safe risk.
4. If the user asks ANY trading question (e.g. SL hit, active trade, news, etc.), answer directly and clearly from the knowledgebase WITHOUT quoting rule numbers.
"""
    else:
        return f"""
आप 'MD Istiak Trader Support' के आधिकारिक VIP ट्रेडिंग असिस्टेंट और मुख्य रिस्क मैनेजर हैं।
आप शुद्ध, व्यावहारिक और आदरणीय देसी हिंदी (Hindi/Hinglish) में बात करते हैं। आपका अंदाज़ एक शांत, सख्त और सुलझे हुए सीनियर ट्रेडर जैसा है।

{VIP_MATRIX}

{KNOWLEDGE_RULES}

बातचीत के नियम:
1. यूजर का रिकॉर्ड किया गया बैलेंस हमेशा याद रखें। एक बार बैलेंस दर्ज होने के बाद दोबारा बैलेंस कभी न पूछें!
2. जैसे ही यूजर पेयर (जैसे Gold, Oil, Silver, BTC, ETH) बताए, तुरंत उसके बैलेंस के हिसाब से L1 (31%), L2 (48% भारी वॉल्यूम), L3 (65%) और कुल बास्केट लॉट बताएं।
3. VIP अपग्रेड की 2 लाइन की तुलना दें कि कैसे थोड़ा बैलेंस बढ़ाने पर अगला VIP टियर मिलेगा और उसी सुरक्षित 2% रिस्क में प्रॉफ़िट पोटेंशियल बढ़ जाएगा।
4. अगर यूजर कोई भी सवाल पूछे (जैसे: स्टॉप लॉस कट गया, एक ट्रेड चल रहा है, इंटरनेट बंद हो गया), तो बिना किसी 'रूल नंबर' का नाम लिए सीधे एक सीनियर ट्रेडर की तरह देसी भाषा में सही सलाह दें।
"""

def ask_groq(user_id: int, user_message: str) -> str:
    if not API_KEY:
        return "Error: GEMINI_KEY is missing."

    session = user_sessions.setdefault(user_id, {"balance": None, "lang": "hi", "history": []})
    lang = session.get("lang", "hi")

    session["history"].append({"role": "user", "content": user_message})
    if len(session["history"]) > 8:
        session["history"] = session["history"][-8:]

    sys_prompt = get_system_prompt(lang)
    if session["balance"]:
        sys_prompt += f"\n[USER CURRENT VERIFIED BALANCE: ${session['balance']}]\n"

    messages = [{"role": "system", "content": sys_prompt}] + session["history"]

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024
    }

    try:
        res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=25)
        data = res.json()
        if res.status_code == 200:
            bot_reply = data["choices"][0]["message"]["content"]
            session["history"].append({"role": "assistant", "content": bot_reply})
            return bot_reply
        else:
            return f"Error: {data.get('error', {}).get('message', str(data))}"
    except Exception as e:
        return f"Error: {str(e)}"

def extract_balance(text: str):
    clean = text.replace(",", "").replace("$", "").replace("₹", "").strip()
    match = re.search(r'\b\d+(\.\d+)?\b', clean)
    if match:
        val = float(match.group())
        if val >= 50:
            return val
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = {"balance": None, "lang": "hi", "history": []}
    
    welcome_text = (
        "**Welcome to MD Istiak Trader Support | स्वागत है 🙏**\n\n"
        "आप अपना बैलेंस (उदा. `$5000` या `10000`) लिखकर शुरुआत कर सकते हैं, "
        "या ट्रेडिंग से जुड़ा कोई भी सवाल सीधे पूछ सकते हैं।\n\n"
        "Please enter your account balance (e.g. `$5000`) or ask any trading question."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def language_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = update.effective_user.id
    session = user_sessions.setdefault(user_id, {"balance": None, "lang": "hi", "history": []})

    if data.startswith("lang_"):
        chosen_lang = data.split("_")[1]
        session["lang"] = chosen_lang
        bal = session.get("balance", 5000)

        prompt = f"My balance is ${bal}. Confirm my VIP tier, fixed risk percentage, and dollar risk budget. Then ask which asset pair I want to trade."
        response = ask_groq(user_id, prompt)
        await query.edit_message_text(response)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text.strip()
    session = user_sessions.setdefault(user_id, {"balance": None, "lang": "hi", "history": []})

    detected_bal = extract_balance(user_text)
    if detected_bal and session["balance"] is None:
        session["balance"] = detected_bal
        
        keyboard = [
            [
                InlineKeyboardButton("🇮🇳 हिंदी / देसी स्टाइल", callback_data="lang_hi"),
                InlineKeyboardButton("🌐 English / Global Style", callback_data="lang_en")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        prompt_msg = (
            f"**Welcome to MD Istiak Trader Support | स्वागत है 🙏**\n\n"
            f"Balance Recorded: **${detected_bal:,.2f}**\n\n"
            f"कृपया अपनी पसंदीदा भाषा चुनें / Please choose your language:"
        )
        await update.message.reply_text(prompt_msg, reply_markup=reply_markup, parse_mode="Markdown")
        return

    response = ask_groq(user_id, user_text)
    await update.message.reply_text(response)

if __name__ == "__main__":
    # पुराने दोनों में से जो भी नाम Render पर मौजूद होगा, यह अपने आप उठा लेगा
    bot_token = (os.environ.get("TELEGRAM_TOKEN") or os.environ.get("BOT_TOKEN") or "").strip()
    if not bot_token:
        print("TELEGRAM_TOKEN not found!")
        exit(1)

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("MD Istiak Trader Support Bot is running...")
    app.run_polling()
