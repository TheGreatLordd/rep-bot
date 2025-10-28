import tomllib
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
LOG_ID = int(os.getenv("LOG_ID"))


with open("config.toml", "rb") as f:
    _config = tomllib.load(f)


PREFIX = _config["bot"]["prefix"]
DB_FILE = _config["bot"]["db_file"]

COOLDOWN = _config["reputation"]["cooldown"]
COOLDOWN_UNIQUE = _config["reputation"]["cooldown_unique"]
RP_GIVE_MINUTES = _config["reputation"]["give_minutes_required"]
REPLY_REP_CD = _config["reputation"]["reply_cooldown"]

LB_SLOTS_SHOWN = _config["leaderboard"]["slots_shown"]

REPUTATION_ROLES = _config["reputation"]["roles"]

THANK_WORDS = ["thank", "thanks", "ty", "thx", "tysm", "thank you"]