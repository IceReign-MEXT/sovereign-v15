import os
import time
import telebot
from threading import Thread
from flask import Flask
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# --- SECURE CONFIGURATION ---
MAIN_TOKEN = os.getenv("TELEGRAM_TOKEN")
GUARD_TOKEN = os.getenv("GUARD_TOKEN")
VAULT = os.getenv("VAULT_WALLET", "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy")

# Initialize Bots
bot_main = telebot.TeleBot(MAIN_TOKEN, threaded=False)
bot_guard = telebot.TeleBot(GUARD_TOKEN, threaded=False)
app = Flask(__name__)

# --- HEALTH CHECK ---
@app.route('/')
@app.route('/health')
def health():
    return {"status": "FLEET_OPERATIONAL", "nodes": "PROTECTOR & GUARD ACTIVE"}, 200

# --- BOT 01: PROTECTOR (Gatekeeper) ---
@bot_main.message_handler(commands=['start'])
def main_start(m):
    msg = (
        "⚔️ **SOVEREIGN V15: PROTECTOR NODE**\n\n"
        "Security Status: **ACTIVE**\n"
        f"Vault: `{VAULT}`\n\n"
        "Official Payment Portal: @Sovereign_Guard_Bot"
    )
    bot_main.reply_to(m, msg, parse_mode='Markdown')

@bot_main.message_handler(func=lambda m: True)
def main_logic(m):
    if len(m.text) >= 32:
        bot_main.reply_to(m, "🔍 **SCANNING...**\nACCESS_DENIED: Verification required via Guard Node.")

# --- BOT 02: GUARD (Verifier) ---
@bot_guard.message_handler(commands=['start'])
def guard_start(m):
    msg = (
        "🛡️ **SOVEREIGN V15: GUARD NODE**\n"
        "----------------------------\n"
        "Official Verification Portal\n\n"
        f"**Burn Tax:** 1.5 SOL\n**Vault:** `{VAULT}`\n\n"
        "Send 1.5 SOL and paste TX Hash to unlock Fleet access."
    )
    bot_guard.reply_to(m, msg, parse_mode='Markdown')

@bot_guard.message_handler(func=lambda m: True)
def guard_logic(m):
    bot_guard.reply_to(m, "📡 **VERIFYING TRANSACTION...**\nStatus: PENDING.")

# --- PERSISTENCE ENGINE ---
def run_bot(bot_instance, name):
    print(f"🚀 {name} INITIALIZING...")
    while True:
        try:
            bot_instance.remove_webhook()
            bot_instance.polling(none_stop=True, interval=2, timeout=60)
        except Exception as e:
            print(f"⚠️ {name} RECOVERY: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # Start Health Server
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()

    # Start Both Bots in Threads
    Thread(target=run_bot, args=(bot_main, "PROTECTOR_NODE")).start()
    Thread(target=run_bot, args=(bot_guard, "GUARD_NODE")).start()
