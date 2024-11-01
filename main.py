import aiohttp
import asyncpg
import asyncio
from os import environ

import discord

from bot import MimeBot

BASE_PREFIX = environ.get("MIME_PREFIX") or "m."


def prefix_callable(bot: MimeBot, msg: discord.Message):
    user_id = bot.user.id  # type: ignore
    return [f"<@!{user_id}> ", f"<@{user_id}> ", BASE_PREFIX]


async def main():
    async with aiohttp.ClientSession() as session:
        return await run_bot(session)


async def run_bot(session: aiohttp.ClientSession):
    pool = await asyncpg.create_pool(environ.get("MIME_PSQL"))
    assert pool is not None

    bot = MimeBot(
        session=session,
        pool=pool,
        command_prefix=prefix_callable,
        intents=discord.Intents(messages=True, message_content=True),
        allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
        case_insensitive=True,
    )

    TOKEN = environ.get("MIME_TOKEN")
    assert TOKEN is not None

    async with bot:
        discord.utils.setup_logging()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
