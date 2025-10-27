import discord
from discord.ext import commands
import logging
import config


class LoggerCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot 
        self.log_channel_id = config.LOG_CHANNEL
        self.logger = logging.getLogger("repbot")
        
    async def send_log(self, message: str, *, embed: discord.Embed = None):
        '''Sends a message or embed to the requested log channel'''
        channel = self.bot.get_channel(config.LOG_CHANNEL)
        await channel.send(content=message, embed=embed) if channel else self.logger.info(f'Channel is not a valid ChannelID or is None. Type: {type(channel)}')
    

async def setup(bot):
    await bot.add_cog(LoggerCog(bot))