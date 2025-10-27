import os, json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
COOLDOWN = int(os.getenv("COOLDOWN", 30))     
COOLDOWN_UNIQUE = int(os.getenv("COOLDOWN_UNIQUE"))
PREFIX = os.getenv("PREFIX")
DB_FILE = os.getenv("DB_FILE")
LOG_CHANNEL = int(os.getenv("LOG_ID"))        
REPUTATION_ROLES = json.loads(os.getenv("REPUTATION_ROLES"))