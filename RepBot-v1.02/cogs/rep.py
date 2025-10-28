import discord
from discord.ext import commands
from datetime import datetime, timedelta
from collections import defaultdict
import aiosqlite
import time
import management.config as config
from cogs.log import LoggerCog
from management.database import DB_FILE
import pytz

COOLDOWN_SECONDS = config.COOLDOWN_UNIQUE

class RepCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.global_cooldowns = {}
        self.per_user_cooldowns = defaultdict(dict)
        self.logger_cog: LoggerCog = bot.get_cog("LoggerCog")

    async def get_user_rep(self, user: discord.Member) -> int:
        async with aiosqlite.connect(DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT reputation FROM users WHERE user_id = ?", (user.id,)) as cursor:
                row = await cursor.fetchone()
                return row["reputation"] if row else 0

    async def add_rep(self, giver_id: int, recipient_id: int, delta: int, ctx: commands.Context):
        guild = ctx.guild
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (recipient_id,))
            await db.execute(
                "UPDATE users SET reputation = reputation + ? WHERE user_id = ?",
                (delta, recipient_id)
            )
            await db.execute(
                "INSERT INTO rep_logs (giver_id, recipient_id, delta) VALUES (?, ?, ?)",
                (giver_id, recipient_id, delta)
            )
            await db.commit()

        new_rep = await self.get_user_rep(guild.get_member(recipient_id))
        await self.update_rep_roles(recipient_id, new_rep)

        if not self.logger_cog:
            self.logger_cog = self.bot.get_cog("LoggerCog")
        if self.logger_cog:
            await self.logger_cog.send_log(
                f'User @{guild.get_member(giver_id).display_name} gave '
                f'@{guild.get_member(recipient_id).display_name} {delta} reputation.'
            )

        await ctx.send(f"Reputation for <@{recipient_id}> changed to {new_rep} successfully!")

    async def update_rep_roles(self, user_id: int, reputation: int):
        guild = self.bot.guilds[0]
        member = guild.get_member(user_id)
        if not member:
            return
        roles_config = {int(k): v for k, v in config.REPUTATION_ROLES.items()}
        target_role_name = None
        for threshold, role_name in sorted(roles_config.items()):
            if reputation >= threshold:
                target_role_name = role_name
        if target_role_name is None:
            target_role_name = roles_config[min(roles_config.keys())]

        for role in member.roles:
            if role.name in roles_config.values():
                await member.remove_roles(role, reason="Reputation role update")
        role = discord.utils.get(guild.roles, name=target_role_name)
        if role:
            await member.add_roles(role, reason="Reputation role update")

    def is_global_cooldown(self, giver_id: int):
        last = self.global_cooldowns.get(giver_id, 0)
        return (time.time() - last) < COOLDOWN_SECONDS

    def is_per_user_cooldown(self, giver_id: int, recipient_id: int):
        last = self.per_user_cooldowns[giver_id].get(recipient_id, 0)
        return (time.time() - last) < config.COOLDOWN

    def update_global_cooldown(self, giver_id: int):
        self.global_cooldowns[giver_id] = time.time()

    def update_per_user_cooldown(self, giver_id: int, recipient_id: int):
        self.per_user_cooldowns[giver_id][recipient_id] = time.time()

    async def verify_rep_sendable(self, ctx: commands.Context, target: discord.Member) -> bool:
        """Check if the target has sent a message in the last X minutes."""
        guild = ctx.guild
        now = discord.utils.utcnow()
        cutoff = now - timedelta(minutes=config.RP_GIVE_MINUTES)
        
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).read_messages:
                try:
                    async for message in channel.history(limit=None, after=cutoff):
                        if message.author.id == target.id:
                            return True
                except (discord.Forbidden, discord.HTTPException):
                    continue
        return False

    @commands.hybrid_command(name="rep", aliases=['gr'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def rep(self, ctx: commands.Context, user: discord.Member, type: str):
        if user.id == ctx.author.id or user.bot:
            return await ctx.message.add_reaction("❌")

        sendable = await self.verify_rep_sendable(ctx, user)
        if not sendable:
            await ctx.send(
                f"{user.display_name} must have sent a message in the last {config.RP_GIVE_MINUTES} minutes.",
                delete_after=6
            )
            return await ctx.message.add_reaction("❌")

        if self.is_global_cooldown(ctx.author.id) or self.is_per_user_cooldown(ctx.author.id, user.id):
            return await ctx.message.add_reaction("⌛")

        delta = 1 if type.lower() == "good" else -1 if type.lower() == "bad" else 0
        if delta == 0:
            return await ctx.message.add_reaction("❌")

        await self.add_rep(ctx.author.id, user.id, delta, ctx)
        self.update_global_cooldown(ctx.author.id)
        self.update_per_user_cooldown(ctx.author.id, user.id)
        await ctx.message.add_reaction("✅")

    @commands.hybrid_command(name="getrep", aliases=['getr'])
    async def getrep(self, ctx: commands.Context, target: discord.Member):
        rep_count = await self.get_user_rep(target)
        await ctx.send(f"{target.display_name} has {rep_count} reputation points.")

    @commands.command(name="leaderboard", aliases=['lb'])
    async def get_leaderboard(self, ctx: commands.Context):
        async with aiosqlite.connect(DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT reputation, user_id FROM users ORDER BY reputation DESC LIMIT 25"
            ) as cursor:
                rows = await cursor.fetchall()
        if not rows:
            return await ctx.send("No leaderboard data found.")

        local_tz = pytz.timezone(config.TIMEZONE) if hasattr(config, "TIMEZONE") else None
        now = datetime.now(tz=local_tz)

        description_lines = []
        for i, row in enumerate(rows[:config.LB_SLOTS_SHOWN], start=1):
            user = self.bot.get_user(row["user_id"])
            name = user.display_name if user else "NA"
            rep = row["reputation"]
            description_lines.append(f"{i}. {name} | {rep} Rep")

        embed = discord.Embed(
            title="Reputation Leaderboard",
            description="\n".join(description_lines),
            colour=0x0084ff,
            timestamp=now
        )
        embed.set_author(name="RepBot")
        embed.set_footer(text="RepBot")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if not message.reference:
            return

        try:
            if message.reference.resolved:
                replied_to_msg = message.reference.resolved
            else:
                replied_to_msg = await message.channel.fetch_message(message.reference.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return

        replied_to: discord.Member = replied_to_msg.author

        if replied_to.bot or replied_to.id == message.author.id:
            return

        if any(word in message.content.lower() for word in config.THANK_WORDS):
            now = time.time()
            last_given = self.per_user_cooldowns[message.author.id].get(replied_to.id, 0)
            if now - last_given < config.REPLY_REP_CD:
                return

            ctx = await self.bot.get_context(message)
            sendable = await self.verify_rep_sendable(ctx, replied_to)
            if not sendable:
                return

            await self.add_rep(message.author.id, replied_to.id, 1, ctx)
            self.per_user_cooldowns[message.author.id][replied_to.id] = now


async def setup(bot):
    await bot.add_cog(RepCog(bot))