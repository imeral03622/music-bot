import discord

#from player.player_manager import get_player
from ui.embeds import create_embed


class PlayerControls(discord.ui.View):

    def __init__(self, player):
        super().__init__(timeout=None)

        self.player = player

    @discord.ui.button(
        label="Skip",
        emoji="<:next:1516106825081159680>",
        style=discord.ButtonStyle.primary
    )
    async def skip_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        voice = interaction.guild.voice_client

        if voice and voice.is_playing():

            voice.stop()

            await interaction.response.send_message(
                embed=create_embed(
                    "Skipped",
                    color=discord.Color.orange()
                ),
                ephemeral=True
            )

    @discord.ui.button(
        label="Repeat",
        emoji="<:repeat:1516109684493516841>",
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
                discord.Color.blurple()
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Stop",
        emoji="<:stop:1516106996552826910>",
        style=discord.ButtonStyle.danger
    )
    async def stop_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        voice = interaction.guild.voice_client

        # player = get_player(
        #     interaction.guild.id
        # )

        self.player.clear_queue()

        if voice:
            voice.stop()

        await interaction.response.send_message(
            embed=create_embed(
                "Stopped",
                color=discord.Color.red()
            ),
            ephemeral=True
        )