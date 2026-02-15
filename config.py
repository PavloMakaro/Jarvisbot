import os
from dotenv import load_dotenv

# Try to load .env file explicitly
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv() # Fallback to default behavior

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set. Please set it in .env or as an environment variable.")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OCR_API_KEY = os.getenv("OCR_API_KEY")
LANGSEARCH_API_KEY = os.getenv("LANGSEARCH_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Base URLs for OpenAI client compatibility
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Default model configuration
DEFAULT_MODEL_PROVIDER = "deepseek"
DEFAULT_MODEL_NAME = "deepseek-chat"

# Database file
DB_FILE = "bot_data.db"
