import asyncio
import re
import time
from urllib.parse import urlparse

import aiohttp

from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_MARKET

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

SPOTIFY_API_URL = "https://api.spotify.com/v1"

SPOTIFY_TRACK_URL_PATTERN = re.compile(
    r"^[A-Za-z0-9]{22}$"
)

HTTP_TIMEOUT = aiohttp.ClientTimeout(
    total=15
)


class SpotifyServiceError(Exception):
    """Base exception for Spotify service errors."""


class SpotifyAuthenticationError(SpotifyServiceError):
    """Raised when Spotify authentication fails."""


class SpotifyTrackNotFoundError(SpotifyServiceError):
    """Raised when the requested Spotify track cannot be found."""


class SpotifyAPIError(SpotifyServiceError):
    """Raised when Spotify API returns an unexpected response."""


_access_token = None
_token_expires_at = 0

_token_lock = asyncio.Lock()


def is_spotify_track_url(url: str) -> bool:
    """
    Check whether the supplied URL points to a single Spotify track.

    Supported examples:

    https://open.spotify.com/track/xxxxxxxxxxxxxxxxxxxxxx

    https://open.spotify.com/track/xxxxxxxxxxxxxxxxxxxxxx?si=...

    Spotify playlist, album, artist and other URLs are not supported.
    """

    try:
        parsed_url = urlparse(url)

        hostname = (
            parsed_url.hostname or ""
        ).lower()

        if hostname not in (
            "open.spotify.com",
            "www.open.spotify.com"
        ):
            return False

        path_parts = [
            part
            for part in parsed_url.path.split("/")
            if part
        ]

        if len(path_parts) != 2:
            return False

        content_type, spotify_id = path_parts

        if content_type != "track":
            return False

        return bool(
            SPOTIFY_TRACK_URL_PATTERN.fullmatch(
                spotify_id
            )
        )

    except Exception:
        return False


async def _get_access_token() -> str:
    """
    Obtain Spotify API access token.

    The token is cached until shortly before expiration.
    """

    global _access_token
    global _token_expires_at

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise SpotifyAuthenticationError(
            "Spotify API credentials are not configured"
        )

    if (
        _access_token
        and time.monotonic() < _token_expires_at
    ):
        return _access_token

    async with _token_lock:

        if (
            _access_token
            and time.monotonic() < _token_expires_at
        ):
            return _access_token

        try:

            async with aiohttp.ClientSession(
                timeout=HTTP_TIMEOUT
            ) as session:

                async with session.post(
                    SPOTIFY_TOKEN_URL,
                    auth=aiohttp.BasicAuth(
                        SPOTIFY_CLIENT_ID,
                        SPOTIFY_CLIENT_SECRET
                    ),
                    data={
                        "grant_type": "client_credentials"
                    }
                ) as response:

                    if response.status != 200:

                        response_text = await response.text()

                        raise SpotifyAuthenticationError(
                            f"Spotify authentication failed: "
                            f"{response.status} - {response_text}"
                        )

                    data = await response.json()

                    access_token = data.get(
                        "access_token"
                    )

                    expires_in = data.get(
                        "expires_in",
                        3600
                    )

                    if not access_token:
                        raise SpotifyAuthenticationError(
                            "Spotify did not return an access token"
                        )

                    _access_token = access_token

                    _token_expires_at = (
                        time.monotonic()
                        + int(expires_in)
                        - 60
                    )

                    return _access_token

        except SpotifyServiceError:
            raise

        except Exception as error:
            raise SpotifyAuthenticationError(
                f"Unable to authenticate with Spotify: {error}"
            ) from error


async def get_spotify_track_query(url: str) -> str:
    """
    Extract Spotify track metadata and build a text search query.

    Returns:

    Artist 1, Artist 2 - Track title
    """

    if not is_spotify_track_url(url):
        raise SpotifyTrackNotFoundError(
            "Invalid Spotify track URL"
        )

    parsed_url = urlparse(url)

    spotify_id = parsed_url.path.rstrip("/").split("/")[-1]

    access_token = await _get_access_token()

    request_url = (
        f"{SPOTIFY_API_URL}/tracks/{spotify_id}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "market": SPOTIFY_MARKET
    }

    try:

        async with aiohttp.ClientSession(
            timeout=HTTP_TIMEOUT
        ) as session:

            async with session.get(
                request_url,
                headers=headers,
                params=params
            ) as response:

                if response.status == 404:
                    raise SpotifyTrackNotFoundError(
                        "Spotify track was not found"
                    )

                if response.status == 401:

                    global _access_token
                    global _token_expires_at

                    _access_token = None
                    _token_expires_at = 0

                    raise SpotifyAuthenticationError(
                        "Spotify access token was rejected"
                    )

                if response.status == 429:

                    retry_after = response.headers.get(
                        "Retry-After",
                        "unknown"
                    )

                    raise SpotifyAPIError(
                        f"Spotify rate limit exceeded. "
                        f"Retry after: {retry_after}"
                    )

                if response.status != 200:

                    response_text = await response.text()

                    raise SpotifyAPIError(
                        f"Spotify API error: "
                        f"{response.status} - {response_text}"
                    )

                data = await response.json()

    except SpotifyServiceError:
        raise

    except Exception as error:
        raise SpotifyAPIError(
            f"Unable to retrieve Spotify track: {error}"
        ) from error

    title = data.get("name")

    artists = data.get(
        "artists",
        []
    )

    artist_names = [
        artist.get("name")
        for artist in artists
        if artist.get("name")
    ]

    if not title or not artist_names:
        raise SpotifyTrackNotFoundError(
            "Spotify track metadata is incomplete"
        )

    artist_string = ", ".join(
        artist_names
    )

    search_query = (
        f"{artist_string} - {title}"
    )

    print(
        f"Spotify track resolved: {search_query}"
    )

    return search_query