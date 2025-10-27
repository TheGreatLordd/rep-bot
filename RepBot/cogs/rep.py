import discord
from discord.ext import commands
import aiosqlite
import time
import config
from collections import defaultdict
from cogs.log import LoggerCog
from database import DB_FILE

COOLDOWN_SECONDS = config.COOLDOWN_UNIQUE

class RepCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.global_cooldowns = {}
        self.per_user_cooldowns = defaultdict(dict)
        self.logger_cog: LoggerCog = bot.get_cog("LoggerCog")

    async def add_rep(self, giver_id: int, recipient_id: int, delta: int, ctx: commands.Context):
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

        async with aiosqlite.connect(DB_FILE) as db:
            async with db.execute("SELECT reputation FROM users WHERE user_id = ?", (recipient_id,)) as cur:
                row = await cur.fetchone()
                new_rep = row[0] if row else 0

        await self.update_rep_roles(recipient_id, new_rep)

        if not self.logger_cog:
            self.logger_cog = self.bot.get_cog("LoggerCog")
        await self.logger_cog.send_log(f'User <@{giver_id}> gave <@{recipient_id}> {delta} reputation.')

        await ctx.send(f"Reputation for <@{recipient_id}> changed to {new_rep} successfully!", delete_after=3.0)
        
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

    @commands.hybrid_command(name="rep", aliases=['gr'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def rep(self, ctx: commands.Context, user: discord.Member, type: str):
        if user.id == ctx.author.id:
            return await ctx.message.add_reaction("❌")

        if self.is_global_cooldown(ctx.author.id):
            return await ctx.message.add_reaction("⌛")
        if self.is_per_user_cooldown(ctx.author.id, user.id):
            return await ctx.message.add_reaction("⌛")

        delta = 1 if type == "good" else -1 if type == "bad" else 0
        if delta == 0:
            return await ctx.message.add_reaction("❌")

        await self.add_rep(ctx.author.id, user.id, delta, ctx)
        self.update_global_cooldown(ctx.author.id)
        self.update_per_user_cooldown(ctx.author.id, user.id)
        await ctx.message.add_reaction("✅")

    @commands.hybrid_command(name="getrep", aliases=['getr'])
    async def getrep(self, ctx: commands.Context, target: discord.Member):
        async with aiosqlite.connect(DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT reputation FROM users WHERE user_id = ?", (target.id,)) as cursor:
                row = await cursor.fetchone()

        rep_count = row["reputation"] if row else 0
        await ctx.send(
            f"{target.display_name} has {rep_count} reputation points.",
            ephemeral=True if hasattr(ctx, "interaction") else False
        )

    @commands.command(name="leaderboard", aliases=['lb'])
    async def get_leaderboard(self, ctx: commands.Context):
        async with aiosqlite.connect(DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT reputation, user_id FROM users ORDER BY reputation DESC LIMIT 25") as cursor:
                rows = await cursor.fetchall()
                if not rows:
                    return
                embed = discord.Embed(title="Reputation Leaderboard", color=discord.Colour.green())
                for i, row in enumerate(rows, start=1):
                    user = self.bot.get_user(row['user_id'])
                    name = user.display_name if user else str(row['user_id'])
                    embed.add_field(
                        name=f"{i}. {name} --- {row['reputation']} rep",
                        value='\u200b',
                        inline=False
                    )
                await ctx.send(embed=embed)

    @commands.command(name="force_give")
    @commands.is_owner()
    async def force_give(self, ctx: commands.Context, recipient: discord.Member, delta: int):
        await self.add_rep(ctx.author.id, recipient.id, delta, ctx)
        await ctx.message.add_reaction("🛡️")

        async with aiosqlite.connect(DB_FILE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT reputation FROM users WHERE user_id = ?", (recipient.id,)) as cursor:
                row = await cursor.fetchone()
                rep = row["reputation"] if row else 0
        await self.update_rep_roles(recipient.id, rep)

    @commands.command(name="set_rep")
    @commands.is_owner()
    async def force_set(self, ctx: commands.Context, target: discord.Member, delta: int):
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("UPDATE users SET reputation = ? WHERE user_id = ?", (delta, target.id))
            await db.commit()
            await ctx.message.add_reaction("🛡️")

        await self.update_rep_roles(target.id, delta)

        if not self.logger_cog:
            self.logger_cog = self.bot.get_cog("LoggerCog")

        if self.logger_cog:
            await self.logger_cog.send_log(f'Administrator <@{ctx.author.id}> force set <@{target.id}> reputation to {delta}.')

async def setup(bot):
    await bot.add_cog(RepCog(bot))
