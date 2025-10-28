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

**Setup instructions:**
1. Open config.toml and edit the variables to your liking
2. Open management > config.py and edit the "THANK_WORDS" list that you want to give rep when someone replies with it.
3. Run the start.bat file, it will create the necessary enviorments./

Files:

------
1. main.py          - Bot entry point
2. config.py        - Configuration file with token, prefix, cooldowns, database file, log channel, and reputation roles
3. database.py      - Database setup (DB_FILE)
4. cogs/
    ├─ log.py       - Logger Cog
    └─ rep.py       - Reputation Cog
    └─ admin.py     - Shutdown cog
    └─utility.py    - A simple wrapper for utility commands such as "help".


Example .env:
-------------
TOKEN=YOUR_BOT_TOKEN_HERE
LOG_ID=YOUR_LOG_CHANNEL_ID_HERE

Bot Permissions:
----------------
The bot requires:
- Send Messages
- Manage Messages (optional, for reactions)
- Manage Roles (to assign reputation roles)
- Read Message History
- Add Reactions



Notes:
------
- Reputation roles are automatically updated based on REPUTATION_ROLES mapping.
- Cooldowns prevent spam giving of reputation.
- **Commands** documentation in the help command when ran.
