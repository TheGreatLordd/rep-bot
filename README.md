RepBot (V1.02)

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
