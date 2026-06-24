import discord
import asyncio
import time

from discord.ext import commands

from config import TOKEN, MAIN_CHANNEL_ID, STATUS_CHANNEL_ID

from commands.music import register_music_commands
from commands.system import register_system_commands

from services.heartbeat_service import (
    heartbeat_loop,
    load_status
)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

register_music_commands(bot)
register_system_commands(bot)


heartbeat_task = None


@bot.event
async def on_ready():
    global heartbeat_task

    print(f"Logged in as {bot.user}")

    # ==============================
    # HEARTBEAT (start only once)
    # ==============================
    if heartbeat_task is None:
        heartbeat_task = asyncio.create_task(
            heartbeat_loop()
        )

    # ==============================
    # CRASH CHECK (power loss detection)
    # ==============================
    status = load_status()

    if (
        status
        and not status.get("clean_shutdown", False)
    ):
        last_seen = status.get("last_seen")

        startup_time = int(time.time())

        downtime = startup_time - last_seen

        channel = bot.get_channel(STATUS_CHANNEL_ID)

        if channel:

            minutes = downtime // 60
            seconds = downtime % 60

            await channel.send(
                "<:highwarning:1519384407700672573> **Unexpected shutdown detected**\n\n"
                f"Last heartbeat: <t:{last_seen}:F>\n"
                f"Recovered: <t:{startup_time}:F>\n"
                f"Downtime: {minutes}m {seconds}s\n\n"
                "<:checkmark:1519385257600749590> Sona is back online and ready to play music again!"
            )

    # ==============================
    # ONE-TIME ANNOUNCEMENT BLOCK
    # ==============================

    # channel = bot.get_channel(MAIN_CHANNEL_ID)

    # if channel:
    #     await channel.send(
    #         "?? Hey everyone!\n\n"
    #         "I'm Sona ? your personal DJ in this server.\n\n"
    #         "I may not be able to join your matches, but I *can* keep your world alive with music ?\n\n"
    #         "Just tell me what you want:\n"
    #         "? /play song name or link\n"
    #         "? /queue to see what's next\n"
    #         "? /skip if you're feeling chaotic\n\n"
    #         "I'm still learning and improving, but I promise to do my best for you ?\n\n"
    #         "Let's make this place sound amazing together ?"
    #     )

    # ==============================
    # END OF ANNOUNCEMENT BLOCK
    # ==============================


bot.run(TOKEN)