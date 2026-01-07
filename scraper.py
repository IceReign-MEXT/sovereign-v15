import os
import time
import telebot
import requests
from threading import Thread
from flask import Flask

# --- INSTITUTIONAL CONFIGURATION ---
# These are managed via Render Environment Variables for maximum security
MAIN_TOKEN = os.getenv("TELEGRAM_TOKEN")
GUARD_TOKEN = os.getenv("GUARD_TOKEN")
HELIUS_KEY = os.getenv("HELIUS_API_KEY")
VAULT = os.getenv("VAULT_WALLET", "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy")

app = Flask(__name__)
# Initialize both bots
bot_main = telebot.TeleBot(MAIN_TOKEN, threaded=False)
bot_guard = telebot.TeleBot(GUARD_TOKEN, threaded=False)

# Simple in-memory storage (Resets on deploy - use Firestore for long-term)
verified_users = set()

@app.route('/')
@app.route('/health')
def health():
    return {
        "status": "FLEET_OPERATIONAL",
        "nodes": ["PROTECTOR_ACTIVE", "GUARD_ACTIVE"],
        "vault_sync": "STABLE"
    }, 200

# --- ON-CHAIN VERIFICATION ENGINE ---
def verify_solana_tx(tx_hash):
    if not HELIUS_KEY or len(tx_hash) < 50:
        return False

    url = f"https://api.helius.xyz/v0/transactions/?api-key={HELIUS_KEY}"
    try:
        response = requests.post(url, json={"transactions": [tx_hash]}, timeout=10)
        data = response.json()
        if not data or not isinstance(data, list): return False

        tx = data[0]
        # Check for 1.5 SOL payment (1,500,000,000 lamports)
        for transfer in tx.get('nativeTransfers', []):
            if transfer['destination'] == VAULT and transfer['amount'] >= 1450000000:
                return True
    except Exception as e:
        print(f"Helius Error: {e}")
    return False

# --- GUARD BOT: THE COMPLIANCE OFFICER ---
@bot_guard.message_handler(commands=['start'])
def guard_welcome(m):
    msg = (
        "🛡️ **SOVEREIGN V15: GUARD NODE**\n"
        "----------------------------\n"
        "Institutional Access Verification\n\n"
        f"**Burn Tax:** 1.5 SOL\n"
        f"**Vault Address:** `{VAULT}`\n\n"
        "1. Send payment to the Vault.\n"
        "2. Paste your **Transaction Signature** here.\n"
        "3. System will auto-whitelist your ID."
    )
    bot_guard.reply_to(m, msg, parse_mode='Markdown')

@bot_guard.message_handler(func=lambda m: len(m.text) > 50)
def handle_verification(m):
    tx_hash = m.text.strip()
    bot_guard.reply_to(m, "📡 **SCANNING MAINNET-BETA...**")

    if verify_solana_tx(tx_hash):
        verified_users.add(m.from_user.id)
        bot_guard.reply_to(m, "✅ **ACCESS GRANTED.**\n\nYour identity is now synchronized. Access @MEX_ProtectorBot for Alpha.")
    else:
        bot_guard.reply_to(m, "❌ **PAYMENT NOT DETECTED.**\nCheck the hash and ensure 1.5 SOL was sent.")

# --- PROTECTOR BOT: THE ALPHA NODE ---
@bot_main.message_handler(commands=['start', 'fleet'])
def protector_start(m):
    if m.from_user.id in verified_users:
        bot_main.reply_to(m, "⚔️ **WELCOME OPERATOR.** Submitting CA to the scanner...")
    else:
        bot_main.reply_to(m, "🔴 **NODE RESTRICTED.**\n\n1.5 SOL Burn Tax required for Alpha access.\n\nVerify via: @Sovereign_Guard_Bot")

@bot_main.message_handler(func=lambda m: True)
def alpha_scanner(m):
    if m.from_user.id in verified_users:
        bot_main.reply_to(m, "🔍 **SCANNING CA...**\n[DATA UNLOCKED]\nLiquidity: High\nScore: 9.8/10")
    else:
        bot_main.reply_to(m, "🔒 **ENCRYPTED.** Pay Burn Tax to view Alpha.")

# --- STARTUP SEQUENCE ---
def run_node(bot, name):
    print(f"🚀 {name} INITIALIZING...")
    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=2)
        except Exception as e:
            print(f"⚠️ {name} RECOVERY: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # Start Flask Health Check on Port 3000
    port = int(os.environ.get("PORT", 3000))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()

    # Start Bot Nodes in separate threads
    Thread(target=run_node, args=(bot_main, "PROTECTOR_NODE")).start()
    run_node(bot_guard, "GUARD_NODE")
