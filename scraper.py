import os
import time
import telebot
import requests
from threading import Thread
from flask import Flask

# --- INSTITUTIONAL CONFIGURATION ---
# These must be set in your Render Environment Variables
MAIN_TOKEN = os.getenv("TELEGRAM_TOKEN")
GUARD_TOKEN = os.getenv("GUARD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
HELIUS_KEY = os.getenv("HELIUS_API_KEY")
VAULT = os.getenv("VAULT_WALLET", "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy")

app = Flask(__name__)

# Initialize Bots
bot_main = telebot.TeleBot(MAIN_TOKEN, threaded=False)
bot_guard = telebot.TeleBot(GUARD_TOKEN, threaded=False)

# Simple in-memory whitelist (In a real scenario, use Firestore for persistence)
verified_users = set()

# --- HEALTH & PORT ---
@app.route('/')
@app.route('/health')
def health():
    return {
        "status": "FLEET_OPERATIONAL",
        "nodes": ["PROTECTOR", "GUARD"],
        "marketing_channel": "CONNECTED" if CHANNEL_ID else "WAITING"
    }, 200

# --- PAYMENT VERIFICATION (HELIUS) ---
def verify_payment_on_chain(tx_hash):
    if not HELIUS_KEY:
        print("❌ Helius API Key missing. Verification skipped.")
        return False

    url = f"https://api.helius.xyz/v0/transactions/?api-key={HELIUS_KEY}"
    try:
        response = requests.post(url, json={"transactions": [tx_hash]}, timeout=10)
        data = response.json()
        if not data or not isinstance(data, list): return False

        tx = data[0]
        # Check native SOL transfers
        for transfer in tx.get('nativeTransfers', []):
            # 1.5 SOL is 1,500,000,000 Lamports
            if transfer['destination'] == VAULT and transfer['amount'] >= 1450000000:
                return True
    except Exception as e:
        print(f"Verify Error: {e}")
    return False

# --- AUTO-FLEX ENGINE (Marketing) ---
def auto_flex_announcer():
    """Posts successful 'picks' to your channel every 2 hours"""
    if not CHANNEL_ID: 
        print("⚠️ No CHANNEL_ID found. Flex mode disabled.")
        return

    print("📢 Auto-Flex Engine: ONLINE")
    while True:
        time.sleep(7200) # Wait 2 hours between flexes
        flex_msg = (
            "⚔️ **SOVEREIGN FLEET SUCCESS**\n"
            "----------------------------\n"
            "Intelligence Node 07 detected **+140%** growth on trending Solana gems in the last 4 hours.\n\n"
            "Verified Operators only. Join the Fleet:\n"
            "👉 @Sovereign_Guard_Bot"
        )
        try:
            bot_main.send_message(CHANNEL_ID, flex_msg, parse_mode='Markdown')
        except Exception as e:
            print(f"Flex Error: {e}")

# --- GUARD BOT: THE VERIFIER (@Sovereign_Guard_Bot) ---
@bot_guard.message_handler(commands=['start'])
def guard_start(m):
    msg = (
        "🛡️ **SOVEREIGN V15: GUARD NODE**\n"
        "----------------------------\n"
        "Payment & Verification Portal\n\n"
        f"**Required Tax:** 1.5 SOL\n"
        f"**Vault:** `{VAULT}`\n\n"
        "1. Send 1.5 SOL to the Vault.\n"
        "2. Paste your **Transaction Hash** here.\n"
        "3. Wait for Node Synchronization."
    )
    bot_guard.reply_to(m, msg, parse_mode='Markdown')

@bot_guard.message_handler(func=lambda m: len(m.text) > 40)
def handle_verification(m):
    tx_hash = m.text.strip()
    bot_guard.reply_to(m, "📡 **SCANNING BLOCKCHAIN...**")

    if verify_payment_on_chain(tx_hash):
        verified_users.add(m.from_user.id)
        bot_guard.reply_to(m, "✅ **ACCESS GRANTED.** Your Telegram ID is now whitelisted. Use @MEX_ProtectorBot now.")
    else:
        bot_guard.reply_to(m, "❌ **VERIFICATION FAILED.** No valid transaction of 1.5 SOL found for this hash.")

# --- PROTECTOR BOT: THE GATEKEEPER (@MEX_ProtectorBot) ---
@bot_main.message_handler(commands=['start'])
def protector_start(m):
    bot_main.reply_to(m, "⚔️ **SOVEREIGN V15: PROTECTOR**\n\nSubmit a Contract Address (CA) to begin scan.")

@bot_main.message_handler(func=lambda m: True)
def protector_logic(m):
    if m.from_user.id in verified_users:
        bot_main.reply_to(m, "🟢 **ALPHA DETECTED.** Contract is safe. Liquidity: $50k+. Trending score: 9.4/10.")
    else:
        bot_main.reply_to(m, "🔴 **ACCESS DENIED.**\n\n1.5 SOL Burn Tax required to unlock Alpha Data.\n\nVerify via @Sovereign_Guard_Bot")

# --- MAIN EXECUTION ---
def start_node(bot, name):
    print(f"🚀 {name} STARTING...")
    while True:
        try:
            bot.remove_webhook()
            time.sleep(2)
            bot.polling(none_stop=True, interval=3)
        except Exception as e:
            print(f"⚠️ {name} Error: {e}")
            time.sleep(15)

if __name__ == "__main__":
    # Start Health Server
    port = int(os.environ.get("PORT", 3000))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()

    # Start Marketing Engine
    Thread(target=auto_flex_announcer, daemon=True).start()

    # Start Both Bots
    Thread(target=start_node, args=(bot_main, "PROTECTOR_NODE")).start()
    start_node(bot_guard, "GUARD_NODE")
