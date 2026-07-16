import asyncio
import time
import discord

from discord.ext import commands

from config import (
    TOKEN,
    MAIN_CHANNEL_ID,
    STATUS_CHANNEL_ID,
    CLOCK_SYNC_DELAY_SECONDS
)

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
    # WAIT FOR SYSTEM CLOCK
    # Gives Raspberry Pi time to
    # synchronize its clock after
    # an unexpected power loss.
    # ==============================
    await asyncio.sleep(CLOCK_SYNC_DELAY_SECONDS)

    # ==============================
    # CRASH CHECK (power loss detection)
    # ==============================
    status = load_status()

    if (
        status
        and not status.get("clean_shutdown", False)
    ):

        last_seen = status.get("last_seen")

        startup_time = await wait_for_clock_sync(last_seen)

        downtime = startup_time - last_seen

        channel = bot.get_channel(
            STATUS_CHANNEL_ID
        )

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
    #         "..."
    #     )

    # ==============================
    # END OF ANNOUNCEMENT BLOCK
    # ==============================


async def wait_for_clock_sync(last_seen: int) -> int:
    """
    Wait until the system clock looks sane after boot.

    Returns current unix timestamp.
    """

    timeout = 120          # maximum wait (seconds)
    safety_margin = 10     # clock must be at least 10 s newer

    start = time.monotonic()

    while True:

        now = int(time.time())

        if now >= last_seen + safety_margin:
            return now

        if time.monotonic() - start >= timeout:
            return now

        await asyncio.sleep(1)

bot.run(TOKEN)