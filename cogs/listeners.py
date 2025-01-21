from __future__ import annotations

from bot import DiscordBot
import discord
from discord.ext import commands
from utils.models import Guild

class Listeners(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.bot.logger.info(f"Bot joined guild: {guild.name} (ID: {guild.id})")

        async with self.bot.redis as redis:
            await redis.hmset(f"guild:{guild.id}", {
                "name": guild.name,
                "member_count": str(guild.member_count),
                "joined_at": str(guild.me.joined_at)
            })

        async with self.bot.db as session:
            guild_info = Guild(
                guild_id=guild.id,
                name=guild.name,
                owner_id=guild.owner_id,
                member_count=guild.member_count,
                is_large=guild.large,
                premium_tier=guild.premium_tier,
                max_members=guild.max_members,
                max_presences=guild.max_presences,
                created_at=guild.created_at
            )
            session.add(guild_info)
            await session.commit()

        self.bot.logger.info(f"Information about guild {guild.name} (ID: {guild.id}) have been added to the database.")

    @commands.Cog.listener()
    async def on_error(self, event: Exception, *args, **kwargs):
        self.bot.logger.error(f"Error in {event}: {args} {kwargs}")
        self.bot.sentry_sdk.capture_exception()

async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Listeners(bot))