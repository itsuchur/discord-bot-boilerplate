from __future__ import annotations

import discord
from discord.ext import commands
import os
from utils.redis_manager import RedisPool
from utils.database import PostgresPool
from datetime import datetime
import config


class DiscordBot(commands.Bot):
    def __init__(self, sentry_sdk = None, logger = None):
        super().__init__(
            command_prefix=os.getenv('BOT_PREFIX', '!'),
            intents=discord.Intents.all(),
            application_id=os.getenv('DISCORD_APP_ID')
        )
        self.uptime = discord.utils.utcnow()
        self.redis = RedisPool()
        self.db = PostgresPool()
        self.sentry_sdk = sentry_sdk
        self.logger = logger
        self.owner_id = 173477542823460864

    async def setup_hook(self):
        """Load cogs and perform initial setup."""
        # Load all cogs from the cogs directory
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    self.logger.info(f"Loaded cog: {filename[:-3]}")
                except Exception as e:
                    self.logger.exception(f"Failed to load cog: {filename[:-3]}. Error: {e}")


        self.logger.info(f'Loaded {len(self.cogs)} cogs')

    def capture_exception(self, exception: Exception):
        self.logger.exception(exception)
        if not config.SENTRY_DSN:
            pass
        else:
            self.sentry_sdk.capture_exception(exception)

    async def on_ready(self):
        self.logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        self.logger.info('------')
        self.logger.info("Invite link...")
        self.logger.info(f"https://discord.com/oauth2/authorize?client_id={config.DISCORD_APP_ID}&permissions=8&integration_type=0&scope=bot")
        self.logger.info('------')

    async def close(self):
        try:
            if hasattr(self, 'redis'):
                await self.redis.pool.disconnect()
                self.logger.info("Redis pool closed successfully")

            if hasattr(self, 'db'):
                await self.db.cleanup()
                self.logger.info("PostgreSQL pool closed successfully")

            # Call parent's close method
            await super().close()
            self.logger.info("Bot shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            self.sentry_sdk.capture_exception(e)