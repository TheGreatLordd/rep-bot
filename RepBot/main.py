import discord
from discord.ext import commands
import config
import database
import logging
import asyncio


logging.basicConfig(
    level=logging.INFO, 
    handlers=[
        logging.FileHandler(filename="repbot.log", encoding="utf-8", mode='w'),
        logging.StreamHandler() 
    ],
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger("repbot")

intents = discord.Intents.default()
intents.members = True            
intents.message_content = True     
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents, case_insensitive=True)

@bot.event
async def on_command_error(ctx: commands.Context, error):
    logger.error(f"Error in command '{ctx.command}': {error}", exc_info=True)
    await ctx.message.add_reaction("❌")

@bot.event
async def on_ready():
    logger.info(f"Bot is online as {bot.user}")

async def main():
    await database.create_db()       
    await bot.load_extension("cogs.rep")
    await bot.load_extension("cogs.admin")
    await bot.load_extension("cogs.log")
    await bot.start(config.TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Bot crashed: {e}", exc_info=True)
