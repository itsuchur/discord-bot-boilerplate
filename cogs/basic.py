from __future__ import annotations
from discord.ext import commands
from sqlalchemy import text


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        async with self.bot.redis as redis:
            guild_info = await redis.hgetall(f"guild:{ctx.guild.id}")

        async with self.bot.db as conn:
            result = await conn.execute(
                text("SELECT name, member_count FROM guilds WHERE guild_id = :guild_id"),
                {"guild_id": ctx.guild.id}
            )
            db_info = result.fetchone()

        response = (
            f"Pong!\n"
            f"Redis Info: Server {guild_info.get('name')} with {guild_info.get('member_count')} members\n"
            f"DB Info: Server {db_info.name} with {db_info.member_count} members"
        )

        await ctx.send(response)

    @commands.command(hidden=True)
    async def reboot(self, ctx):
        if ctx.author.id != self.bot.owner_id:
            raise commands.MissingPermissions
        await ctx.send("Rebooting...")
        await self.bot.close()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        self.bot.logger.error(f"Command error in {ctx.command}: {error}")
        self.bot.sentry_sdk.capture_exception(error)

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        else:
            await ctx.send("An error occurred while processing the command.")


async def setup(bot):
    await bot.add_cog(Basic(bot))
