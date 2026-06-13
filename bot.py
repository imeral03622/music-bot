import discord
from discord.ext import commands
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

music_queue = []

current_track = None
current_url = None

loop_mode = False

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


@bot.event
async def on_ready():
    print(f"bot started: {bot.user}")


async def play_song(ctx, url):
    global current_track
    global current_url

    voice = ctx.voice_client

    def get_stream():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            return (
                info["url"],
                info.get("title", "unknown")
            )

    stream_url, title = await bot.loop.run_in_executor(
        None,
        get_stream
    )

    current_track = title
    current_url = url

    source = discord.FFmpegOpusAudio(
        stream_url,
        **FFMPEG_OPTIONS
    )

    voice.play(
        source,
        after=lambda e: bot.loop.create_task(
            play_next(ctx)
        )
    )

    await ctx.send(f"now playing: {title}")


async def play_next(ctx):
    global loop_mode
    global current_url

    if loop_mode and current_url:
        await play_song(ctx, current_url)
        return

    if not music_queue:
        return

    next_url = music_queue.pop(0)

    await play_song(ctx, next_url)


@bot.command()
async def play(ctx, url: str):

    if not ctx.voice_client:
        if not ctx.author.voice:
            await ctx.send("You are not in a voice channel")
            return

        channel = ctx.author.voice.channel
        await channel.connect()

    voice = ctx.voice_client

    if voice.is_playing():
        music_queue.append(url)

        await ctx.send(
            f"added to queue (position {len(music_queue)})"
        )
        return

    await play_song(ctx, url)


@bot.command()
async def queue(ctx):

    if not music_queue:
        await ctx.send("queue is empty")
        return

    message = "queue:\n"

    for index, url in enumerate(
        music_queue,
        start=1
    ):
        message += f"{index}. {url}\n"

    await ctx.send(message)


@bot.command()
async def nowplaying(ctx):

    if not current_track:
        await ctx.send("nothing is playing")
        return

    await ctx.send(
        f"now playing: {current_track}"
    )


@bot.command()
async def skip(ctx):

    if not ctx.voice_client:
        return

    if not ctx.voice_client.is_playing():
        return

    ctx.voice_client.stop()

    await ctx.send("skipped")


@bot.command()
async def clear(ctx):

    music_queue.clear()

    await ctx.send("queue cleared")


@bot.command()
async def remove(ctx, position: int):

    if position < 1:
        await ctx.send("invalid position")
        return

    if position > len(music_queue):
        await ctx.send("invalid position")
        return

    removed = music_queue.pop(position - 1)

    await ctx.send(
        f"removed: {removed}"
    )


@bot.command()
async def loop(ctx):
    global loop_mode

    loop_mode = not loop_mode

    if loop_mode:
        await ctx.send("loop enabled")
    else:
        await ctx.send("loop disabled")


@bot.command()
async def stop(ctx):

    music_queue.clear()

    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("stopped")


@bot.command()
async def leave(ctx):
    global current_track
    global current_url
    global loop_mode

    music_queue.clear()

    current_track = None
    current_url = None

    loop_mode = False

    if ctx.voice_client:
        await ctx.voice_client.disconnect()

    await ctx.send("disconnected")


bot.run(TOKEN)