from discord import app_commands

from ytmusicapi import YTMusic


ytmusic = YTMusic()


async def autocomplete_tracks(
    bot,
    current: str
):

    if len(current) < 2:
        return []

    def search():

        results = ytmusic.search(
            current,
            filter="songs",
            limit=10
        )

        tracks = []

        for item in results:

            title = item.get(
                "title",
                "Unknown"
            )

            artists = ", ".join(
                artist["name"]
                for artist in item.get(
                    "artists",
                    []
                )
            )

            tracks.append(
                (
                    f"{title} - {artists}",
                    item["videoId"]
                )
            )

        return tracks

    return await bot.loop.run_in_executor(
        None,
        search
    )


async def play_autocomplete(
    interaction,
    current: str
):

    try:

        bot = interaction.client

        tracks = await autocomplete_tracks(
            bot,
            current
        )

        return [
            app_commands.Choice(
                name=name[:100],
                value=video_id
            )
            for name, video_id
            in tracks[:15]
        ]

    except Exception:

        return []