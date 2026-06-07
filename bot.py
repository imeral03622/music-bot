import discord
from discord.ext import commands
import yt_dlp
import os

TOKEN = "MTA3NDczODc0NTY5OTQ3NTQ1Ng.GtVMJZ.IwdwwyvLz6xmQAtP7XNQ-h58Y-9WDoBONQ-AE0"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True
}


FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


@bot.event
async def on_ready():
    print(f"bot started: {bot.user}")


@bot.command()
async def play(ctx, url: str):
    # 1. auto-join logic
    if not ctx.voice_client:
        if not ctx.author.voice:
            await ctx.send("You are not in a voice channel")
            return

        channel = ctx.author.voice.channel
        await channel.connect()

    voice = ctx.voice_client

    # 2. yt-dlp extract
    def get_stream():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            return info['url'], info.get('title', 'unknown')

    stream_url, title = await bot.loop.run_in_executor(None, get_stream)

    # 3. play audio
    source = discord.FFmpegOpusAudio(stream_url, **FFMPEG_OPTIONS)

    voice.stop()
    voice.play(source)

    await ctx.send(f"now playing: {title}")


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
