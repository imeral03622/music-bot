from typing import cast

import discord

from commands.command_utils import send_error, send_success
from data.constants import COLORS, MESSAGES
from player.player_manager import get_player
from ui.embeds import create_embed


def register_player_commands(bot):

    @bot.tree.command(
        name="nowplaying",
        description="Show current track"
    )
    async def nowplaying(
        interaction: discord.Interaction
    ):

        if interaction.guild is None:
            await send_error(
                interaction,
                "This command can only be used in a server."
            )

            return

        player = get_player(
            interaction.guild.id
        )

        if player.current_track is None:

            await send_success(
                interaction,
                "Nothing Playing",
                MESSAGES["nothing_playing"]
            )

            return

        embed = player.current_track.create_embed()

        embed.set_author(
            name="Now Playing"
        )

        embed.add_field(
            name="Repeat",
            value=(
                "Enabled"
                if player.repeat_mode
                else "Disabled"
            ),
            inline=True
        )

        await interaction.response.send_message(
            embed=embed
        )

    @bot.tree.command(
        name="skip",
        description="Skip current track"
    )
    async def skip(
        interaction: discord.Interaction
    ):

        assert interaction.guild is not None
        voice_client = interaction.guild.voice_client

        if voice_client is None:

            await send_error(
                interaction,
                MESSAGES["bot_not_connected"]
            )

            return

        if not cast(discord.VoiceClient, voice_client).is_playing():

            await send_error(
                interaction,
                MESSAGES["nothing_playing"]
            )

            return

        cast(discord.VoiceClient, voice_client).stop()

        await send_success(
            interaction,
            "Skipped",
            "Track skipped"
        )

    @bot.tree.command(
        name="repeat",
        description="Toggle repeat mode"
    )
    async def repeat(
        interaction: discord.Interaction
    ):

        assert interaction.guild is not None
        player = get_player(
            interaction.guild.id
        )

        player.repeat_mode = (
            not player.repeat_mode
        )

        await interaction.response.send_message(
            embed=create_embed(
                "Repeat",
                (
                    "Enabled"
                    if player.repeat_mode
                    else "Disabled"
                ),
                COLORS["info"]
            )
        )

    @bot.tree.command(
        name="stop",
        description="Stop playback"
    )
    async def stop(
        interaction: discord.Interaction
    ):

        assert interaction.guild is not None
        player = get_player(
            interaction.guild.id
        )

        player.repeat_mode = False
        player.clear_queue()

        voice_client = interaction.guild.voice_client

        if voice_client is not None:
            cast(discord.VoiceClient, voice_client).stop()

        await send_success(
            interaction,
            "Stopped",
            "Playback stopped"
        )

    @bot.tree.command(
        name="leave",
        description="Disconnect bot"
    )
    async def leave(
        interaction: discord.Interaction
    ):

        assert interaction.guild is not None
        player = get_player(
            interaction.guild.id
        )

        voice_client = interaction.guild.voice_client

        player.clear_queue()
        player.current_track = None
        player.repeat_mode = False

        if voice_client is not None:
            await voice_client.disconnect(force=True)

        await send_success(
            interaction,
            "Disconnected",
            "Bot disconnected"
        )