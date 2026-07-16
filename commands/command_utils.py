import discord

from data.constants import (
    COLORS
)

from ui.embeds import create_embed


async def send_error(
    interaction: discord.Interaction,
    message: str
):
    await interaction.response.send_message(
        embed=create_embed(
            "Error",
            message,
            COLORS["error"]
        )
    )


async def send_followup_error(
    interaction: discord.Interaction,
    message: str
):
    await interaction.followup.send(
        embed=create_embed(
            "Error",
            message,
            COLORS["error"]
        )
    )


async def send_success(
    interaction: discord.Interaction,
    title: str,
    description: str = "",
    color: discord.Color = COLORS["success"]
):
    await interaction.response.send_message(
        embed=create_embed(
            title,
            description,
            color
        )
    )