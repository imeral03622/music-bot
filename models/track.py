from dataclasses import dataclass

import discord


@dataclass
class Track:

    title: str
    url: str
    webpage_url: str
    duration: int
    thumbnail: str | None
    source: str

    def duration_string(self) -> str:

        if not self.duration:
            return "unknown"

        minutes = self.duration // 60
        seconds = self.duration % 60

        return f"{minutes}:{seconds:02d}"

    def create_embed(self) -> discord.Embed:

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

        embed.add_field(
            name="Source",
            value=self.source,
            inline=True
        )

        if self.thumbnail:
            embed.set_thumbnail(
                url=self.thumbnail
            )

        return embed

    def __str__(self) -> str:
        return self.title