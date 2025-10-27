RepBot - Discord Reputation Bot
===============================

Description:
-------------
RepBot is a Discord bot that allows users to give and track reputation points.
It supports commands for giving reputation, viewing leaderboards, 
automatic reputation role assignment, and administrative commands 
to set or give reputation.

Requirements:
-------------
- Python 3.11+ (tested on 3.13)
- pip
- A Discord bot token with appropriate permissions (see below)
- A server where the bot can manage roles and send messages

Python Dependencies:
-------------------
Install the following packages in your virtual environment:

    pip install -U discord.py aiosqlite python-dotenv

Files:
------
1. main.py          - Bot entry point
2. config.py        - Configuration file with token, prefix, cooldowns, database file, log channel, and reputation roles
3. database.py      - Database setup (DB_FILE)
4. cogs/
    ├─ log.py       - Logger Cog
    └─ rep.py       - Reputation Cog
    └─ admin.py       - Shutdown cog

Environment Variables (.env):
-----------------------------
- TOKEN           : Your Discord bot token
- PREFIX          : Command prefix (e.g., "!")
- COOLDOWN        : Cooldown per user for giving rep (seconds)
- COOLDOWN_UNIQUE : Global cooldown for all users (seconds)
- DB_FILE         : SQLite database file path (e.g., "rep.db")
- LOG_ID          : Discord channel ID for logging actions
- REPUTATION_ROLES: JSON mapping of thresholds to role names
                   Example:
                   {"-25": "Bad Rep", "25": "Good Rep", "50": "Great Rep", "100": "Amazing Rep"}

Example .env:
-------------
TOKEN=YOUR_BOT_TOKEN_HERE
PREFIX=!
COOLDOWN=30
COOLDOWN_UNIQUE=60
DB_FILE=rep.db
LOG_ID=123456789012345678
REPUTATION_ROLES={"-25": "Bad Rep", "25": "Good Rep", "50": "Great Rep", "100": "Amazing Rep"}

Bot Permissions:
----------------
The bot requires:
- Send Messages
- Manage Messages (optional, for reactions)
- Manage Roles (to assign reputation roles)
- Read Message History
- Add Reactions


Commands:
---------
User Commands:
- [prefix]rep <@user> <good/bad> : Give rep to a user
- [prefix]getrep <@user>         : Check a user's reputation
- [prefix]leaderboard             : Show top 25 users by reputation

Admin Commands (bot owner only):
- [prefix]force_give <@user> <amount> : Give reputation to a user
- [prefix]set_rep <@user> <amount>    : Set a user's reputation
- Logs for admin actions are sent to LOG_ID channel.

Notes:
------
- Reputation roles are automatically updated based on REPUTATION_ROLES mapping.
- Cooldowns prevent spam giving of reputation.