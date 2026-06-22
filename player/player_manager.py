from player.music_player import MusicPlayer

players: dict[int, MusicPlayer] = {}


def get_player(
    guild_id: int
) -> MusicPlayer:

    if guild_id not in players:
        players[guild_id] = MusicPlayer()

    return players[guild_id]


def remove_player(
    guild_id: int
) -> None:

    if guild_id in players:
        del players[guild_id]