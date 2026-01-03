import os
import time
import telebot
from threading import Thread
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
VAULT = os.getenv("VAULT_WALLET", "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy")

# Use a non-threaded bot for the cloud to prevent internal conflicts
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return {"status": "FLEET_OPERATIONAL"}, 200

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def welcome(m):
    bot.reply_to(m, f"⚔️ **SOVEREIGN V15 ONLINE**\n\n**Vault:** `{VAULT}`", parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def handle_input(m):
    if len(m.text) >= 32:
        bot.reply_to(m, "🔍 SCANNING... \nRESULT: 1.5 SOL TAX NOT PAID.")

def start_bot():
    # THE NUCLEAR OPTION: Remove any existing webhooks or polling sessions
    print("🧹 CLEARING GHOST CONNECTIONS...")
    bot.remove_webhook()
    time.sleep(2)

    print("🚀 SOVEREIGN FLEET V15: ONLINE")
    while True:
        try:
            # Long polling with a limit of 1 instance
            bot.polling(none_stop=True, interval=3, timeout=60)
        except Exception as e:
            print(f"⚠️ RECOVERY: {e}")
            time.sleep(10)

if __name__ == "__main__":
    Thread(target=run_health_server, daemon=True).start()
    start_bot()
