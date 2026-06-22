import discord

from discord import app_commands

from player.player_manager import get_player
from ui.embeds import create_embed
from ui.controls import PlayerControls
from services.youtube_service import (
    get_track_info,
    search_track
)
from services.autocomplete_service import (
    play_autocomplete
)


def register_music_commands(bot):

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

        if not interaction.user.voice:

            await interaction.followup.send(
                embed=create_embed(
                    "Error",
                    "You are not in a voice channel",
                    discord.Color.red()
                )
            )

            return

        voice_client = interaction.guild.voice_client

        if not voice_client:

            channel = interaction.user.voice.channel

            voice_client = await channel.connect()

        try:

            if query.startswith(
                ("http://", "https://")
            ):
                track = await get_track_info(
                    query
                )

            else:
                track = await search_track(
                    query
                )

        except Exception as e:

            print(e)

            await interaction.followup.send(
                embed=create_embed(
                    "Error",
                    "Unable to load this track",
                    discord.Color.red()
                )
            )

            return

        if voice_client.is_playing():

            player.add_to_queue(track)

            embed = create_embed(
                "Added to Queue",
                track.title,
                discord.Color.orange()
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
                discord.Color.blurple()
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

    @bot.tree.command(
        name="queue",
        description="Show current queue"
    )
    async def queue(
        interaction: discord.Interaction
    ):
        player = get_player(
            interaction.guild.id
        )

        if not player.queue:

            await interaction.response.send_message(
                embed=create_embed(
                    "Queue",
                    "Queue is empty",
                    discord.Color.orange()
                )
            )

            return

        embed = create_embed(
            "Queue",
            color=discord.Color.green()
        )

        for index, track in enumerate(
            player.queue,
            start=1
        ):
            embed.add_field(
                name=f"{index}. {track.title}",
                value=f"Duration: {track.duration_string()}",
                inline=False
            )

        await interaction.response.send_message(
            embed=embed
        )

    @bot.tree.command(
        name="nowplaying",
        description="Show current track"
    )
    async def nowplaying(
        interaction: discord.Interaction
    ):
        player = get_player(
            interaction.guild.id
        )

        if not player.current_track:

            await interaction.response.send_message(
                embed=create_embed(
                    "Nothing Playing",
                    "No track is currently playing",
                    discord.Color.orange()
                )
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
        voice_client = interaction.guild.voice_client

        if not voice_client:

            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Bot is not connected",
                    discord.Color.red()
                )
            )

            return

        if not voice_client.is_playing():

            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Nothing is playing",
                    discord.Color.red()
                )
            )

            return

        voice_client.stop()

        await interaction.response.send_message(
            embed=create_embed(
                "Skipped",
                "Track skipped",
                discord.Color.orange()
            )
        )

    @bot.tree.command(
        name="clear",
        description="Clear queue"
    )
    async def clear(
        interaction: discord.Interaction
    ):
        player = get_player(
            interaction.guild.id
        )

        player.clear_queue()

        await interaction.response.send_message(
            embed=create_embed(
                "Queue Cleared",
                color=discord.Color.orange()
            )
        )

    @bot.tree.command(
        name="remove",
        description="Remove track from queue"
    )
    @app_commands.describe(
        position="Track number in queue"
    )
    async def remove(
        interaction: discord.Interaction,
        position: int
    ):
        player = get_player(
            interaction.guild.id
        )

        if position < 1 or position > len(player.queue):

            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Invalid position",
                    discord.Color.red()
                )
            )

            return

        removed = player.remove_track(
            position - 1
        )

        await interaction.response.send_message(
            embed=create_embed(
                "Removed",
                removed.title,
                discord.Color.orange()
            )
        )

    @bot.tree.command(
        name="repeat",
        description="Toggle repeat mode"
    )
    async def repeat(
        interaction: discord.Interaction
    ):
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
                discord.Color.blurple()
            )
        )

    @bot.tree.command(
        name="stop",
        description="Stop playback"
    )
    async def stop(
        interaction: discord.Interaction
    ):
        player = get_player(
            interaction.guild.id
        )

        player.repeat_mode = False

        player.clear_queue()

        voice_client = interaction.guild.voice_client

        if voice_client:
            voice_client.stop()

        await interaction.response.send_message(
            embed=create_embed(
                "Stopped",
                "Playback stopped",
                discord.Color.orange()
            )
        )

    @bot.tree.command(
        name="leave",
        description="Disconnect bot"
    )
    async def leave(
        interaction: discord.Interaction
    ):
        player = get_player(
            interaction.guild.id
        )

        voice_client = interaction.guild.voice_client

        player.clear_queue()
        player.current_track = None
        player.repeat_mode = False

        if voice_client:
            await voice_client.disconnect()

        await interaction.response.send_message(
            embed=create_embed(
                "Disconnected",
                "Bot disconnected",
                discord.Color.orange()
            )
        )