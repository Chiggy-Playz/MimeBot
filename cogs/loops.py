from discord.ext import commands, tasks
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import MimeBot


class Loops(commands.Cog):
    def __init__(self, bot: "MimeBot"):
        self.bot = bot

    async def cog_load(self) -> None:
        self.loop.start()

    @tasks.loop(hours=12)
    async def loop(self):
        asset_count = await self.bot.pool.fetchval("SELECT COUNT(*) FROM assets")
        print("Fetched asset count:", asset_count)

    @loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot: "MimeBot"):
    await bot.add_cog(Loops(bot))
