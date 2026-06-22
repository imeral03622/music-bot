import discord

from config import BOT_VERSION


def create_embed(
    title,
    description=None,
    color=discord.Color.blue()
):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    embed.set_footer(
        text=f"Music Bot v{BOT_VERSION}"
    )

    return embed