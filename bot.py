import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import yt_dlp
import os
import re

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found")

BOT_VERSION = "0.0.7"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

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

class Track:

    def __init__(
        self,
        title,
        url,
        webpage_url,
        stream_url,
        duration,
        thumbnail
    ):
        self.title = title
        self.url = url
        self.webpage_url = webpage_url
        self.stream_url = stream_url
        self.duration = duration
        self.thumbnail = thumbnail

    def duration_string(self):

        if not self.duration:
            return "unknown"

        minutes = self.duration // 60
        seconds = self.duration % 60

        return f"{minutes}:{seconds:02d}"

    def __str__(self):
        return self.title

    def create_embed(self):

        embed = discord.Embed(
            title=self.title,
            url=self.webpage_url,
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Duration",
            value=self.duration_string(),
            inline=True
        )

        if self.thumbnail:
            embed.set_thumbnail(
                url=self.thumbnail
            )

        return embed

class MusicPlayer:

    def __init__(self):
        self.queue = []
        self.current_track = None
        self.repeat_mode = False

    async def play_song(self, channel, track):

        voice = discord.utils.get(
            bot.voice_clients,
            guild=channel.guild
        )

        self.current_track = track

        source = discord.FFmpegOpusAudio(
            track.stream_url,
            **FFMPEG_OPTIONS
        )

        voice.play(
            source,
            after=lambda e: bot.loop.create_task(
                self.play_next(channel)
            )
        )

        embed = track.create_embed()

        embed.set_author(
            name="Now Playing"
        )

        await channel.send(
            embed=embed,
            view=PlayerControls()
        )

    async def play_next(self, channel):

        if self.repeat_mode and self.current_track:

            await self.play_song(
                channel,
                self.current_track
            )

            return

        if not self.queue:
            return

        next_track = self.queue.pop(0)

        await self.play_song(
            channel,
            next_track
        )

    def add_to_queue(self, track):
        self.queue.append(track)


    def clear_queue(self):
        self.queue.clear()


    def remove_track(self, position):
        return self.queue.pop(position)

    players = {}

def get_player(guild_id):

    if guild_id not in players:
        players[guild_id] = MusicPlayer()

    return players[guild_id]

players = {}


class PlayerControls(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Skip",
        emoji="<:next:1516106825081159680>",#"\U000023ED",
        style=discord.ButtonStyle.primary
    )
    async def skip_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        voice = interaction.guild.voice_client

        if voice and voice.is_playing():

            voice.stop()

            await interaction.response.send_message(
                embed=create_embed(
                    "Skipped",
                    color=discord.Color.orange()
                ),
                ephemeral=True
            )

    @discord.ui.button(
        label="repeat",
        emoji="<:repeat:1516109684493516841>",#"\U0001F501",
        style=discord.ButtonStyle.secondary
    )
    async def repeat_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        player = get_player(
            interaction.guild.id
        )

        player.repeat_mode = (
            not player.repeat_mode
        )

        await interaction.response.send_message(
            embed=create_embed(
                "repeat",
                (
                    "Enabled"
                    if player.repeat_mode
                    else "Disabled"
                ),
                discord.Color.blurple()
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Stop",
        emoji="<:stop:1516106996552826910>",#"\U000023F9",
        style=discord.ButtonStyle.danger
    )
    async def stop_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        voice = interaction.guild.voice_client

        player = get_player(
            interaction.guild.id
        )

        player.clear_queue()

        if voice:
            voice.stop()

        await interaction.response.send_message(
            embed=create_embed(
                "Stopped",
                color=discord.Color.red()
            ),
            ephemeral=True
        )


@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()

        print(
            f"synced {len(synced)} commands"
        )

    except Exception as e:
        print(e)

    print(f"bot started: {bot.user}")

async def get_track_info(query):

    def extract():

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:

            if query.startswith("http://") or query.startswith("https://"):

                info = ydl.extract_info(
                    query,
                    download=False
                )

            else:

                info = ydl.extract_info(
                    f"ytsearch1:{query}",
                    download=False
                )

                info = info["entries"][0]

            return Track(
                title=info.get(
                    "title",
                    "unknown"
                ),

                url=query,

                webpage_url=info.get(
                    "webpage_url",
                    query
                ),

                stream_url=info.get(
                    "url"
                ),

                duration=info.get(
                    "duration",
                    0
                ),

                thumbnail=info.get(
                    "thumbnail"
                )
            )

    return await bot.loop.run_in_executor(
        None,
        extract
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
        color=discord.Color.green()
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


@bot.tree.command(
    name="play",
    description="Play a song or add it to queue"
)
@app_commands.describe(
    query="Song name or YouTube URL"
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

    track = await get_track_info(query)

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

    await interaction.followup.send(
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

        embed = create_embed(
            "Queue",
            "Queue is empty",
            discord.Color.orange()
        )

        await interaction.response.send_message(
            embed=embed
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

        embed = create_embed(
            "Nothing Playing",
            "No track is currently playing",
            discord.Color.orange()
        )

        await interaction.response.send_message(
            embed=embed
        )

        return

    embed = player.current_track.create_embed()

    embed.set_author(
        name="Now Playing"
    )

    embed.add_field(
        name="repeat",
        value="Enabled" if player.repeat_mode else "Disabled",
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

        embed = create_embed(
            "Error",
            "Bot is not connected",
            discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed
        )

        return

    if not voice_client.is_playing():

        embed = create_embed(
            "Error",
            "Nothing is playing",
            discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed
        )

        return

    voice_client.stop()

    embed = create_embed(
        "Skipped",
        "Track skipped",
        discord.Color.orange()
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

    embed = create_embed(
        "Queue Cleared",
        color=discord.Color.orange()
    )

    await interaction.response.send_message(
        embed=embed
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

    if position < 1:

        embed = create_embed(
            "Error",
            "Invalid position",
            discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed
        )

        return

    if position > len(player.queue):

        embed = create_embed(
            "Error",
            "Invalid position",
            discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed
        )

        return

    removed = player.remove_track(
        position - 1
    )

    embed = create_embed(
        "Removed",
        removed.title,
        discord.Color.orange()
    )

    await interaction.response.send_message(
        embed=embed
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

    player.repeat_mode = not player.repeat_mode

    embed = create_embed(
        "repeat",
        (
            "repeat enabled"
            if player.repeat_mode
            else "repeat disabled"
        ),
        discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed
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

    voice_client = interaction.guild.voice_client

    player.clear_queue()

    if voice_client:
        voice_client.stop()

    embed = create_embed(
        "Stopped",
        "Playback stopped",
        discord.Color.orange()
    )

    await interaction.response.send_message(
        embed=embed
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

    embed = create_embed(
        "Disconnected",
        "Bot disconnected",
        discord.Color.orange()
    )

    await interaction.response.send_message(
        embed=embed
    )


bot.run(TOKEN)
