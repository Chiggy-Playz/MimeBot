from discord.ext import commands

import aiohttp
import asyncpg
import jishaku


class MimeBot(commands.Bot):
    session: aiohttp.ClientSession
    pool: asyncpg.Pool

    def __init__(self, session: aiohttp.ClientSession, pool: asyncpg.Pool, *args, **kwargs):
        self.session = session
        self.pool = pool

        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")
        await self.load_extension("cogs.mime")

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")