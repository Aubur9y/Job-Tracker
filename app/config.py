import os
from dotenv import load_dotenv

load_dotenv()
def load_config():
    return {
        "MONGO_URI": os.getenv("MONGO_URI"),
        "HEADLESS": False,
    }