import discord
from discord.ext import commands
from cogs.rep import RepCog
import management.config as config

class UtilityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rep_cog: RepCog = bot.get_cog("RepCog")  # reference existing RepCog

    @commands.hybrid_command(name="help")
    async def help(self, ctx: commands.Context):
        """Provides a written Discord embed documentation for RepBot."""
        ctx.message.add_reaction("✅")
        embed = discord.Embed(
            title="RepBot Commands Documentation",
            description="Here are the commands you can use:",
            color=0x00FF00  
        )

        embed.add_field(
            name=f"{config.PREFIX}rep @[user] [good/bad]",
            value="Adds or removes rep.\n- `good` → +1 rep\n- `bad` → -1 rep\n- Cannot rep yourself.",
            inline=False
        )

        embed.add_field(
            name=f"{config.PREFIX}leaderboard",
            value="Displays the leaderboard showing top users by rep.",
            inline=False
        )

        embed.add_field(
            name=f"{config.PREFIX}getrep @[user]",
            value="Shows the total rep for a user. Defaults to yourself if no user is provided.",
            inline=False
        )

        embed.add_field(
            name=f"{config.PREFIX}compare @[user1] @[user2]",
            value="Compares the rep between two specified users.",
            inline=False
        )

        embed.add_field(
            name=f"{config.PREFIX}myrank",
            value="Sends your current leaderboard rank along with the user above and below your current rank.",
            inline=False
        )

        embed.set_author(name="RepBot")
        embed.set_footer(text="Help")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))  
