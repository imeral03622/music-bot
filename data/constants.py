import discord


EMOJIS = {

    "skip":
        "<:next:1516106825081159680>",

    "repeat":
        "<:repeat:1516109684493516841>",

    "stop":
        "<:stop:1516106996552826910>",

}


MESSAGES = {

    "queue_empty":
        "Queue is empty",

    "nothing_playing":
        "No track is currently playing",

    "not_in_voice":
        "You are not in a voice channel",

    "bot_not_connected":
        "Bot is not connected",

    "track_load_error":
        "Unable to load this track",

    "invalid_position":
        "Invalid position",

}


COLORS = {

    "error":
        discord.Color.red(),

    "success":
        discord.Color.orange(),

    "info":
        discord.Color.blurple(),

    "queue":
        discord.Color.green(),

    "track":
        discord.Color.blue(),

}