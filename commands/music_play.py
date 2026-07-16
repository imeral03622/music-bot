import discord

from discord import app_commands

from player.player_manager import get_player

from services.youtube_service import (
    get_track_info,
    search_track
)

from services.autocomplete_service import (
    play_autocomplete
)

from ui.embeds import create_embed

from data.constants import (
    COLORS,
    MESSAGES
)

from commands.command_utils import (
    send_followup_error
)


def register_play_command(bot):

    @bot.tree.command(
        name="play",
        description="Play a song or add it to queue"
    )
    @app_commands.describe(
        query="Song name or YouTube URL"
    )
    @app_commands.autocomplete(
        query=play_autocomplete
    )
    async def play(
        interaction: discord.Interaction,
        query: str
    ):

        player = get_player(
            interaction.guild.id
        )

        await interaction.response.defer()

        if interaction.user.voice is None:

            await send_followup_error(
                interaction,
                MESSAGES["not_in_voice"]
            )

            return

        voice_client = interaction.guild.voice_client

        if voice_client is None:

            voice_client = await (
                interaction.user.voice.channel.connect()
            )

        try:

            if query.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                track = await get_track_info(
                    query
                )

            else:

                track = await search_track(
                    query
                )

        except Exception as error:

            print(error)

            await send_followup_error(
                interaction,
                MESSAGES["track_load_error"]
            )

            return

        if voice_client.is_playing():

            player.add_to_queue(
                track
            )

            embed = create_embed(
                "Added to Queue",
                track.title,
                COLORS["success"]
            )

            if track.thumbnail:

                embed.set_thumbnail(
                    url=track.thumbnail
                )

            await interaction.followup.send(
                embed=embed
            )

            return

        loading_message = await interaction.followup.send(
            embed=create_embed(
                "Loading...",
                track.title,
                COLORS["info"]
            )
        )

        await player.play_song(
            interaction.channel,
            track
        )

        try:

            await loading_message.delete()

        except Exception:
            pass