import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OCR_API_KEY = os.getenv("OCR_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Base URLs for OpenAI client compatibility
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Default model configuration
DEFAULT_MODEL_PROVIDER = "deepseek"
DEFAULT_MODEL_NAME = "deepseek-chat"

# Database file
DB_FILE = "bot_data.db"
