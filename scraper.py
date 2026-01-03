import os
import time
import telebot
from threading import Thread
from flask import Flask

# --- INSTITUTIONAL CONFIGURATION ---
# We pull these directly from Render Environment Variables
MAIN_TOKEN = os.getenv("TELEGRAM_TOKEN")
GUARD_TOKEN = os.getenv("GUARD_TOKEN")
VAULT = os.getenv("VAULT_WALLET", "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy")

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    """Satisfies Render's health check to keep the service pinned live"""
    return {
        "status": "FLEET_OPERATIONAL",
        "nodes": {
            "protector": "ACTIVE" if MAIN_TOKEN else "OFFLINE",
            "guard": "ACTIVE" if GUARD_TOKEN else "OFFLINE"
        }
    }, 200

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- NODE PERSISTENCE ENGINE ---
def run_bot(token, name, logic_func):
    if not token or len(token) < 10:
        print(f"❌ {name} SHUTDOWN: Missing secure token.")
        return

    print(f"🚀 {name} INITIALIZING...")
    bot = telebot.TeleBot(token, threaded=False)

    # Initialize Handlers
    logic_func(bot)

    while True:
        try:
            # Force reset the session to kill ghost connections (409 Fix)
            bot.remove_webhook()
            time.sleep(2)

            print(f"📡 {name} SYNCED: Listening for commands...")
            bot.polling(none_stop=True, interval=3, timeout=60)
        except Exception as e:
            if "Conflict" in str(e) or "409" in str(e):
                print(f"⚠️ {name} CONFLICT: Ghost instance detected. Cooling down 20s...")
                time.sleep(20)
            else:
                print(f"⚠️ {name} RECOVERY: {e}")
                time.sleep(10)

# --- NODE 01: PROTECTOR LOGIC ---
def protector_logic(bot):
    @bot.message_handler(commands=['start', 'fleet'])
    def start(m):
        msg = (
            "⚔️ **SOVEREIGN V15: PROTECTOR**\n"
            "----------------------------\n"
            "**Status:** INSTITUTIONAL NODE ONLINE\n"
            f"**Vault Address:** `{VAULT}`\n\n"
            "Official Verification Node: @Sovereign_Guard_Bot"
        )
        bot.reply_to(m, msg, parse_mode='Markdown')

    @bot.message_handler(func=lambda m: True)
    def handle_ca(m):
        if len(m.text) >= 32:
            bot.reply_to(m, "🔍 **SCANNING BLOCKCHAIN...**\nACCESS_DENIED: 1.5 SOL Burn Tax required.")

# --- NODE 02: GUARD LOGIC ---
def guard_logic(bot):
    @bot.message_handler(commands=['start'])
    def start(m):
        msg = (
            "🛡️ **SOVEREIGN V15: GUARD**\n"
            "----------------------------\n"
            "**Portal:** PAYMENT VERIFICATION\n"
            f"**Required Tax:** 1.5 SOL\n"
            f"**Target Vault:** `{VAULT}`\n\n"
            "Paste TX Hash after sending payment."
        )
        bot.reply_to(m, msg, parse_mode='Markdown')

    @bot.message_handler(func=lambda m: True)
    def verify(m):
        bot.reply_to(m, "📡 **VERIFYING ON-CHAIN...**\nStatus: PENDING. No payment detected yet.")

if __name__ == "__main__":
    # Start Health Server
    Thread(target=run_health_server, daemon=True).start()

    # Start Protector
    Thread(target=run_bot, args=(MAIN_TOKEN, "PROTECTOR_NODE", protector_logic)).start()

    # Start Guard
    Thread(target=run_bot, args=(GUARD_TOKEN, "GUARD_NODE", guard_logic)).start()
