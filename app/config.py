import os
from dotenv import load_dotenv

load_dotenv()
def load_config():
    return {
        "MONGO_URI": os.getenv("MONGO_URI"),
        "HEADLESS": False,
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    }