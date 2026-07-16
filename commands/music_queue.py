import discord

from discord import app_commands

from player.player_manager import get_player

from ui.embeds import create_embed

from data.constants import (
    COLORS,
    MESSAGES
)

from commands.command_utils import (
    send_error,
    send_success
)


def register_queue_commands(bot):

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

            await send_success(
                interaction,
                "Queue",
                MESSAGES["queue_empty"]
            )

            return

        embed = create_embed(
            "Queue",
            color=COLORS["queue"]
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

        await send_success(
            interaction,
            "Queue Cleared"
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

        if not (
            1 <= position <= len(player.queue)
        ):

            await send_error(
                interaction,
                MESSAGES["invalid_position"]
            )

            return

        removed = player.remove_track(
            position - 1
        )

        await send_success(
            interaction,
            "Removed",
            removed.title
        )