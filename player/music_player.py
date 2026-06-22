import asyncio
import discord

from config import (
    AUTO_DISCONNECT_SECONDS,
    FFMPEG_OPTIONS
)

from services.youtube_service import (
    get_fresh_stream_url
)

from models.track import Track

from ui.controls import PlayerControls


class MusicPlayer:

    def __init__(self):

        self.queue: list[Track] = []

        self.current_track: Track | None = None

        self.repeat_mode = False

        self.disconnect_task = None

        self.player_message = None

    def add_to_queue(
        self,
        track: Track
    ) -> None:

        self.queue.append(track)

    def clear_queue(self) -> None:

        self.queue.clear()

    def remove_track(
        self,
        position: int
    ) -> Track:

        return self.queue.pop(position)

    async def disable_player_message(
        self
    ):

        if not self.player_message:
            return

        try:

            await self.player_message.edit(
                view=None
            )

        except Exception:
            pass

        self.player_message = None

    async def play_song(
        self,
        channel,
        track: Track
    ):

        voice = channel.guild.voice_client

        loop = asyncio.get_running_loop()

        if not voice:
            return

        self.current_track = track

        await self.disable_player_message()

        if self.disconnect_task:

            self.disconnect_task.cancel()

            self.disconnect_task = None

        stream_url = await get_fresh_stream_url(
            track.webpage_url
        )

        source = discord.FFmpegPCMAudio(
            stream_url,
            **FFMPEG_OPTIONS
        )

        voice.play(
            source,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(channel),
                loop
            )
        )

        embed = track.create_embed()

        embed.set_author(
            name="Now Playing"
        )

        self.player_message = await channel.send(
            embed=embed,
            view=PlayerControls(self)
        )

    async def play_next(
        self,
        channel
    ):

        if self.repeat_mode and self.current_track:

            await self.play_song(
                channel,
                self.current_track
            )

            return

        if not self.queue:

            await self.disable_player_message()

            if self.disconnect_task:
                self.disconnect_task.cancel()

            self.disconnect_task = asyncio.create_task(
                self.auto_disconnect(
                    channel.guild
                )
            )

            return

        next_track = self.queue.pop(0)

        await self.play_song(
            channel,
            next_track
        )

    async def auto_disconnect(
        self,
        guild
    ):

        await asyncio.sleep(
            AUTO_DISCONNECT_SECONDS
        )

        voice = guild.voice_client

        if not voice:
            return

        if voice.is_playing():
            return

        if self.queue:
            return

        await voice.disconnect()

        self.current_track = None

        self.repeat_mode = False

        print(
            f"Disconnected from {guild.name} because of inactivity"
        )