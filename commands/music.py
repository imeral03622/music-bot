from commands.music_play import (
    register_play_command
)

from commands.music_queue import (
    register_queue_commands
)

from commands.music_player import (
    register_player_commands
)


def register_music_commands(bot):

    register_play_command(bot)
    register_queue_commands(bot)
    register_player_commands(bot)