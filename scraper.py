import os
import time
import telebot
from threading import Thread
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

# --- SECURE CONFIGURATION ---
MAIN_TOKEN = os.getenv("TELEGRAM_TOKEN")
GUARD_TOKEN = os.getenv("GUARD_TOKEN")
VAULT = os.getenv("VAULT_WALLET", "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy")

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return {"status": "FLEET_OPERATIONAL", "main_node": bool(MAIN_TOKEN), "guard_node": bool(GUARD_TOKEN)}, 200

# --- PERSISTENCE ENGINE ---
def run_bot(token, name, logic_func):
    if not token:
        print(f"❌ {name} SKIPPED: Token missing in environment.")
        return

    print(f"🚀 {name} INITIALIZING...")
    bot = telebot.TeleBot(token, threaded=False)

    # Apply logic based on node name
    logic_func(bot)

    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=2, timeout=60)
        except Exception as e:
            print(f"⚠️ {name} RECOVERY: {e}")
            time.sleep(10)

# --- NODE LOGIC ---
def protector_logic(bot):
    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m, f"⚔️ **SOVEREIGN V15: PROTECTOR**\nVault: `{VAULT}`", parse_mode='Markdown')

    @bot.message_handler(func=lambda m: True)
    def handle(m):
        if len(m.text) >= 32:
            bot.reply_to(m, "🔍 **SCANNING...**\nACCESS_DENIED: Verification required via Guard Node.")

def guard_logic(bot):
    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m, f"🛡️ **SOVEREIGN V15: GUARD**\nTax: 1.5 SOL\nVault: `{VAULT}`", parse_mode='Markdown')

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()

    # Start Protector
    Thread(target=run_bot, args=(MAIN_TOKEN, "PROTECTOR_NODE", protector_logic)).start()

    # Start Guard
    Thread(target=run_bot, args=(GUARD_TOKEN, "GUARD_NODE", guard_logic)).start()
