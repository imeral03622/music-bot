import yt_dlp
import asyncio

from config import YDL_OPTIONS

from models.track import Track

async def get_track_info(
    query: str
) -> Track:

    def extract():

        with yt_dlp.YoutubeDL(
            YDL_OPTIONS
        ) as ydl:

            if query.startswith(
                ("http://", "https://")
            ):

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
                url=info.get(
                    "original_url"
                ) or query,
                webpage_url=info.get(
                    "webpage_url"
                ) or query,
                duration=info.get(
                    "duration",
                    0
                ),
                thumbnail=info.get(
                    "thumbnail"
                ),
                source=info.get(
                    "extractor_key",
                    "Unknown"
                )
            )

    return await asyncio.to_thread(
        extract
    )

async def get_fresh_stream_url(
    youtube_url: str
) -> str:

    def extract():

        ydl_opts = {
            "format": "bestaudio[ext=webm]/bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android",
                        "web"
                    ]
                }
            }
        }

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                youtube_url,
                download=False
            )

            formats = info.get(
                "formats",
                []
            )

            audio_formats = [
                fmt
                for fmt in formats
                if fmt.get("acodec") != "none"
                and fmt.get("vcodec") == "none"
            ]

            best = (
                audio_formats[-1]
                if audio_formats
                else None
            )

            return (
                best or info
            ).get("url")

    return await asyncio.to_thread(
        extract
    )


async def search_track(
    query: str
) -> Track:

    def extract():

        with yt_dlp.YoutubeDL(
            YDL_OPTIONS
        ) as ydl:

            search_sources = [
                f"ytsearch3:{query}"
            ]

            for source in search_sources:

                source_name = (
                    "SoundCloud"
                    if source.startswith(
                        "scsearch"
                    )
                    else "YouTube"
                )

                try:

                    info = ydl.extract_info(
                        source,
                        download=False
                    )

                    if not info:
                        continue

                    entries = info.get(
                        "entries",
                        []
                    )

                    best_entry = None

                    for entry in entries:

                        duration = int(
                            entry.get(
                                "duration",
                                0
                            ) or 0
                        )

                        if duration >= 60:
                            best_entry = entry
                            break

                    if (
                        not best_entry
                        and entries
                    ):
                        best_entry = entries[0]

                    if not best_entry:
                        continue

                    return Track(
                        title=best_entry.get(
                            "title",
                            "unknown"
                        ),
                        url=query,
                        webpage_url=best_entry.get(
                            "webpage_url",
                            query
                        ),
                        duration=int(
                            best_entry.get(
                                "duration",
                                0
                            ) or 0
                        ),
                        thumbnail=best_entry.get(
                            "thumbnail"
                        ),
                        source=source_name
                    )

                except Exception:
                    continue

            raise Exception(
                "No search results"
            )

    return await asyncio.to_thread(
        extract
    )