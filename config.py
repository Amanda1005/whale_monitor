import os
from dotenv import load_dotenv 

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


OI_CHANGE_THRESHOLD = 10_000_000  
CHECK_INTERVAL = 300


WATCH_COINS = ["BTC", "ETH"]