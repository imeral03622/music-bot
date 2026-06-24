import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found")

BOT_VERSION = "0.1.1"

GUILD_ID = 1055384191459659817

STATUS_CHANNEL_ID = 1519370336351686670

MAIN_CHANNEL_ID = 1055384191459659820

AUTO_DISCONNECT_SECONDS = 900

YDL_OPTIONS = {
    "format": "bestaudio[ext=webm]/bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    # "extractor_args": {
    #     "youtube": {
    #         "player_client": ["android"]
    #     }
    # }
}

FFMPEG_OPTIONS = {
    "before_options": (
        "-reconnect 1 "
        "-reconnect_streamed 1 "
        "-reconnect_delay_max 5"
    ),
    "options": "-vn"
}