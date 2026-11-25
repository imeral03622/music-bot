import discord

from data.constants import COLORS, EMOJIS
from ui.embeds import create_embed


class PlayerControls(discord.ui.View):

    def __init__(self, player):
        super().__init__(timeout=None)

        self.player = player

    @discord.ui.button(
        label="Skip",
        emoji=EMOJIS["skip"],
        style=discord.ButtonStyle.primary
    )
    async def skip_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        assert interaction.guild is not None
        voice = interaction.guild.voice_client

        if isinstance(voice, discord.VoiceClient) and voice.is_playing():

            voice.stop()

            await interaction.response.send_message(
                embed=create_embed(
                    "Skipped",
                    color=COLORS["success"]
                ),
                ephemeral=True
            )

    @discord.ui.button(
        label="Repeat",
        emoji=EMOJIS["repeat"],
        style=discord.ButtonStyle.secondary
    )
    async def repeat_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        # player = get_player(
        #     interaction.guild.id
        # )

        self.player.repeat_mode = (
            not self.player.repeat_mode
        )

        await interaction.response.send_message(
            embed=create_embed(
                "Repeat",
                (
                    "Enabled"
                    if self.player.repeat_mode
                    else "Disabled"
                ),
                COLORS["info"]
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Stop",
        emoji=EMOJIS["stop"],
        style=discord.ButtonStyle.danger
    )
    async def stop_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        assert interaction.guild is not None
        voice = interaction.guild.voice_client

        self.player.clear_queue()

        if isinstance(voice, discord.VoiceClient):
            voice.stop()

        await interaction.response.send_message(
            embed=create_embed(
                "Stopped",
                color=COLORS["error"]
            ),
            ephemeral=True
        )