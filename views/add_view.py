from typing import Any, Coroutine, Optional
import discord
from discord.interactions import Interaction
from discord.ui import Select, View, Button

from models.asset import Asset, AssetType
from main import MimeBot


class AddAssetsDropdown(Select):
    assets: list[Asset]

    def __init__(self, assets: list[Asset]):
        self.assets = assets

        options = [
            discord.SelectOption(
                label=f"{asset.asset_type.name} {asset.asset_id}",
                value=str(i),
                emoji=discord.PartialEmoji.from_str(f"name_{i}:{asset.asset_id}")
                if asset.asset_type == AssetType.emoji
                else None,
            )
            for i, asset in enumerate(assets)
        ]

        super().__init__(
            placeholder="Select emojis to add to your collection",
            options=options,
            max_values=len(options),
        )

    async def callback(self, interaction: Interaction[MimeBot]):
        await interaction.response.send_message("Selecting", ephemeral=True)


class AddAssetsView(View):
    dropdowns: list[AddAssetsDropdown]
    selected_assets: list[Asset] | None

    def __init__(self, assets: list[Asset], timeout: float | None = 180):
        super().__init__(timeout=timeout)

        # Based on the number of assets, add upto 4 dropdowns or error out
        # Add a dropdown for each 25 assets
        # If there are more than 100 assets, error out
        # Add buttons in the last row to confirm or cancel

        if len(assets) > 100:
            raise ValueError("Cannot add more than 100 assets at once")

        if len(assets) == 0:
            raise ValueError("No assets provided")

        dropdowns = [AddAssetsDropdown(assets[i : i + 25]) for i in range(0, len(assets), 25)]

        for dropdown in dropdowns:
            self.add_item(dropdown)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Confirming", ephemeral=True)
        self.selected_assets = []
        for dropdown in self.dropdowns:
            self.selected_assets.extend(map(lambda i: dropdown.assets[int(i)], dropdown.values))
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.selected_assets = None
        self.stop()
