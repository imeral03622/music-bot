import discord

from ui.embeds import create_embed
from config import GUILD_ID
from data.constants import COLORS


def register_system_commands(bot):

    @bot.event
    async def on_ready():

        try:

            guild = discord.Object(
                id=GUILD_ID
            )

            bot.tree.clear_commands(
                guild=guild
            )

            await bot.tree.sync(
                guild=guild
            )

            synced = await bot.tree.sync()

            print(
                f"synced {len(synced)} commands"
            )

        except Exception as e:
            print(e)

        print(
            f"bot started: {bot.user}"
        )

    @bot.tree.command(
        name="help",
        description="Show all commands"
    )
    async def help_command(
        interaction: discord.Interaction
    ):

        embed = create_embed(
            "Music Bot Commands",
            color=COLORS["info"]
        )

        embed.add_field(
            name="/play",
            value="Play song or add to queue",
            inline=False
        )

        embed.add_field(
            name="/queue",
            value="Show queue",
            inline=False
        )

        embed.add_field(
            name="/nowplaying",
            value="Current song",
            inline=False
        )

        embed.add_field(
            name="/skip",
            value="Skip current song",
            inline=False
        )

        embed.add_field(
            name="/remove",
            value="Remove track from queue",
            inline=False
        )

        embed.add_field(
            name="/clear",
            value="Clear queue",
            inline=False
        )

        embed.add_field(
            name="/repeat",
            value="Toggle repeat mode",
            inline=False
        )

        embed.add_field(
            name="/stop",
            value="Stop playback",
            inline=False
        )

        embed.add_field(
            name="/leave",
            value="Disconnect bot",
            inline=False
        )

        await interaction.response.send_message(
            embed=embed
        )