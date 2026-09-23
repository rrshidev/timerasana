import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_URL = os.getenv("API_URL", "http://localhost:8000")
TIMER_BOT_KEY = os.getenv("TIMER_BOT_KEY", "")