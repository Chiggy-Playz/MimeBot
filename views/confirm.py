import discord


class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Alright", ephemeral=True)
        self.value = True
        self.stop()
        await interaction.message.delete()  # type: ignore

    @discord.ui.button(label="No", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Nope, Got it", ephemeral=True)
        self.value = False
        self.stop()
        await interaction.message.delete()  # type: ignore
