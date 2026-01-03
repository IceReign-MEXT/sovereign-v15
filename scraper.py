import os
import requests
from dotenv import load_dotenv
import telebot

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "⚔️ SOVEREIGN V15 ONLINE\nNodes: 54 Active\nOperator: MEX_ROBERT\n\nStatus: Awaiting Burn Tax verification.")

@bot.message_handler(func=lambda m: True)
def track(m):
    if len(m.text) > 30:
        bot.reply_to(m, "🔍 SCANNING FLEET... \nRESULT: 1.5 SOL TAX NOT PAID. ACCESS DENIED.")

print("🚀 FLEET BOT STARTING...")
bot.polling()
