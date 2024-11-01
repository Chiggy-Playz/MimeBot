from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import re
from bot import MimeBot

from models.asset import Asset, AssetType
from views.confirm import ConfirmView

ASSET_REGEX = (

    # Match emojis url
    r"emojis/(?P<emojiLinkId>[0-9]+)\.(?P<emojiExtension>[a-zA-Z]+)(?:\?.*?&?name=(?P<emojiLinkName>[a-zA-Z0-9_\- ]+)?)?"
    # Match stickers url
    r"|stickers/(?P<stickerLinkId>[0-9]+)\.(?P<stickerExtension>[a-zA-Z]+)(?:\?.*?&?name=(?P<stickerName>[a-zA-Z0-9_\- ]+)?)?"
    # Match raw emoji
    r"|<(?P<emojiAnimated>(a)?):(?P<emojiName>[a-zA-Z0-9_\- ]+):(?P<emojiId>[0-9]+)>"
)


def parse_assets(content: str) -> list[Asset]:
    matches = re.finditer(ASSET_REGEX, content, re.MULTILINE)

    parsed_assets: list[Asset] = []
    for match in matches:
        groups = match.groupdict()

        if groups["emojiLinkId"] is not None:
            asset_type = AssetType.emoji
            asset_id = int(groups["emojiLinkId"])
            animated = groups["emojiExtension"] == "gif"
            asset_name = groups["emojiLinkName"] or str(asset_id)
        elif groups["stickerLinkId"] is not None:
            asset_type = AssetType.sticker
            asset_id = int(groups["stickerLinkId"])
            # Probably never gonna happen since gif sticker's are uploaded as attachments
            animated = groups["stickerExtension"] == "gif"
            asset_name = groups["stickerName"] or str(asset_id)
        else:  # It's _probably_ <:name:id>
            asset_type = AssetType.emoji
            asset_id = int(groups["emojiId"])
            animated = groups["emojiAnimated"] != ""
            asset_name = groups["emojiName"] or str(asset_id)

        asset = Asset(asset_type, asset_id, asset_name, animated)

        if asset in parsed_assets:
            continue
        parsed_assets.append(asset)
    return parsed_assets


class MimeCog(commands.Cog):
    bot: MimeBot

    def __init__(self, bot: MimeBot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Add to collection",
            callback=self.add_from_context,
            allowed_contexts=app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True),
            allowed_installs=app_commands.AppInstallationType(guild=True, user=True),
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    @commands.command(name="add")
    async def add(self, context: commands.Context[MimeBot], *args) -> None:
        """Add emojis to your collection"""

        # Check if args provided or replied to message
        if len(args) == 0 and context.message.reference is None:
            await context.send("You must specify at least one emoji or reply to a message containing emojis!")
            return

        # Parse args and replied message content for emojis / stickers

        content = " ".join(args)
        parsed_assets = parse_assets(content)

        # If replied to message, ask the user if they want to add the replied message's content to their collection
        if context.message.reference is not None:
            confirm_view = ConfirmView()
            confirm_message = await context.send("Would you like to add from the replied message?", view=confirm_view)
            await confirm_view.wait()

            if confirm_view.value is True:
                replied_message = await context.fetch_message(context.message.reference.message_id)  # type: ignore
                parsed_assets += parse_assets(replied_message.content)

            await confirm_message.delete()

        # If no emojis were found, send an error message
        if len(parsed_assets) == 0:
            await context.send("No emojis were found!")
            return

        # Add assets to all assets and then to user's unassigned assets

        await context.bot.pool.executemany(
            "INSERT INTO assets (id, type, animated) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            [
                (
                    asset.asset_id,
                    asset.asset_type.name,
                    asset.animated,
                )
                for asset in parsed_assets
            ],
        )

        await context.bot.pool.executemany(
            "INSERT INTO unassigned_assets (user_id, asset_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            [
                (
                    context.author.id,
                    asset.asset_id,
                )
                for asset in parsed_assets
            ],
        )

        await context.send(f"Added {len(parsed_assets)} emoji(s) to your collection!")

    async def add_from_context(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.defer(ephemeral=True)

        # Parse args and replied message content for emojis / stickers
        parsed_assets = parse_assets(message.content)

        # If replied to message, ask the user if they want to add the replied message's content to their collection
        if message.reference is not None:
            confirm_view = ConfirmView()
            await interaction.followup.send(
                "Would you like to add from the replied message?", view=confirm_view, ephemeral=True
            )
            await confirm_view.wait()

            if confirm_view.value is True:
                replied_message = await context.fetch_message(context.message.reference.message_id)  # type: ignore
                parsed_assets += parse_assets(replied_message.content)

        # If no emojis were found, send an error message
        if len(parsed_assets) == 0:
            await interaction.followup.send("No emojis were found!", ephemeral=True)
            return

        # Add assets to all assets and then to user's unassigned assets

        await self.bot.pool.executemany(
            "INSERT INTO assets (id, type, animated) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            [
                (
                    asset.asset_id,
                    asset.asset_type.name,
                    asset.animated,
                )
                for asset in parsed_assets
            ],
        )

        await self.bot.pool.executemany(
            "INSERT INTO unassigned_assets (user_id, asset_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            [
                (
                    interaction.user.id,
                    asset.asset_id,
                )
                for asset in parsed_assets
            ],
        )

        await interaction.followup.send(f"Added {len(parsed_assets)} emoji(s) to your collection!", ephemeral=True)


async def setup(bot: MimeBot) -> None:
    await bot.add_cog(MimeCog(bot))
