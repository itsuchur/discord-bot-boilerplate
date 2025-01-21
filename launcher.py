from __future__ import annotations

import asyncio
from dotenv import load_dotenv

import config
from bot import DiscordBot
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sqlalchemy.ext.asyncio import create_async_engine
from loguru import logger
from utils.models import Base
from datetime import datetime

load_dotenv()

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def init_sentry():
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        traces_sample_rate=1.0,
        integrations=[
            AsyncioIntegration(),
        ],
    )
    return sentry_sdk

start_up_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logger.add(f"logs/discord-bot-started-{start_up_time_str}.log", format="{time} {level} {message}", rotation="200 MB")


async def init_database():
    engine = create_async_engine(config.DB_HOST)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables checked/created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sentry_sdk.capture_exception(e)
    finally:
        await engine.dispose()


async def main():
    try:
        sentry = init_sentry()
        await init_database()
        bot = DiscordBot(sentry_sdk=sentry, logger=logger)
        await bot.start(config.DISCORD_TOKEN)
    except Exception as e:
        logger.exception("Bot crashed:")
        sentry_sdk.capture_exception(e)


if __name__ == '__main__':
    asyncio.run(main())