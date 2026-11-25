import asyncio
import logging
from typing import Any, cast

import yt_dlp

from config import YDL_OPTIONS
from models.track import Track

logger = logging.getLogger(__name__)


class NoSearchResultsError(Exception):
    """Raised when yt-dlp returns no usable search results."""


async def get_track_info(
    query: str
) -> Track:

    def extract():

        with yt_dlp.YoutubeDL(
            cast(Any, YDL_OPTIONS)
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

                entries = list(cast(Any, info.get("entries") or []))
                if not entries:
                    raise NoSearchResultsError("No track found")
                info = entries[0]

            title = info.get("title") or "unknown"
            duration = int(info.get("duration") or 0)

            return Track(
                title=title,
                url=info.get(
                    "original_url"
                ) or query,
                webpage_url=info.get(
                    "webpage_url"
                ) or query,
                duration=duration,
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
            cast(Any, ydl_opts)
        ) as ydl:

            info = ydl.extract_info(
                youtube_url,
                download=False
            )

            formats = info.get(
                "formats",
                [],
            ) or []

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

            stream_url = (
                best or info
            ).get("url")

            if not isinstance(stream_url, str):
                raise TypeError("No audio stream URL found")

            return stream_url

    return await asyncio.to_thread(
        extract
    )


async def search_track(
    query: str
) -> Track:

    def extract():

        with yt_dlp.YoutubeDL(
            cast(Any, YDL_OPTIONS)
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

                    entries = list(cast(Any, info.get("entries") or []))

                    best_entry = None

                    for entry in entries:

                        if not entry:
                            continue

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

                    title = best_entry.get("title") or "unknown"
                    webpage_url = best_entry.get("webpage_url") or query

                    return Track(
                        title=title,
                        url=query,
                        webpage_url=webpage_url,
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

                except yt_dlp.utils.DownloadError:
                    logger.exception("YouTube search failed for %r", query)
                    continue

            raise NoSearchResultsError(
                "No search results"
            )

    return await asyncio.to_thread(
        extract
    )