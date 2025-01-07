import discord


class EmbedView(discord.ui.View):
    def __init__(
        self,
        embed: discord.Embed,
        label: str = None,
        style: discord.ButtonStyle = discord.ButtonStyle.primary,
    ):
        super().__init__(timeout=180)  # Optional: add a timeout for the view
        self.embed = embed
        self.label = label if label is not None else embed.title

        # Create the button with the given label and style
        self.button = discord.ui.Button(label=label, style=style)
        self.button.callback = self.show_settings
        self.add_item(self.button)

    async def show_settings(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self.embed, ephemeral=True)
