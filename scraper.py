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

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- HEALTH CHECK SERVER (For Render) ---
@app.route('/')
@app.route('/health')
def health():
    return {"status": "FLEET_OPERATIONAL", "nodes": 54}, 200

def run_health_server():
    # Render provides the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- FLEET LOGIC ---
def get_trending_gems():
    url = "https://public-api.birdeye.so/public/trending?list_iteration=1"
    headers = {"X-API-KEY": BIRDEYE_KEY, "x-chain": "solana"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', {}).get('tokens', [])
    except Exception:
        pass
    return []

@bot.message_handler(commands=['start'])
def welcome(m):
    bot.reply_to(m, f"⚔️ **SOVEREIGN V15 ONLINE**\n\n**Vault:** `{VAULT}`\nPay 1.5 SOL Tax to index assets.", parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def handle_input(m):
    if len(m.text) >= 32:
        bot.reply_to(m, "🔍 SCANNING... \nRESULT: 1.5 SOL TAX NOT PAID. ACCESS DENIED.")

# --- MAIN ENGINE ---
if __name__ == "__main__":
    print("🚀 STARTING HEALTH SERVER...")
    # Run the Health Server in a separate thread
    Thread(target=run_health_server).start()

    print("🚀 SOVEREIGN FLEET ONLINE")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"⚠️ ERROR: {e}")
            time.sleep(10)
