import discord
from discord.ext import commands

from config import TOKEN
from commands.music import register_music_commands
from commands.system import register_system_commands

intents = discord.Intents.default()
intents.message_content = True  # it can be removed if we don't use prefix commands.

bot = commands.Bot(
    command_prefix="!",  # legacy, you can then remove it completely if we go to slash-only
    intents=intents
)

register_music_commands(bot)
register_system_commands(bot)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # ==============================
    # ONE-TIME ANNOUNCEMENT BLOCK
    # ==============================

    # channel_id = 00000000  # channel ID

    # channel = bot.get_channel(channel_id)

    # if channel:
    #     await channel.send(
    #         "<:musicanime:1518498881330090075><a:heartsparkles:1518503745577812040> Hey everyone!\n\n"

    #         "Sona has entered the lobby. <:blueneonheart:1518504663006052462>\n\n"
            
    #         "I may not be able to queue up for a match with you, but I can still be part of the team in my own way.\n\n"
            
    #         "My job is simple: keep the music flowing, set the mood, and make every gaming session a little more memorable. <a:dance2:1515984924933623808>\n\n"

    #         "Need chill vibes? I've got you.\n"
    #         "Need something energetic? I've got you.\n"
    #         "Need the same song on repeat until everyone goes slightly insane? ...I've got you! <:vibes:1515976295593414867>\n\n"

    #         "I'm currently running version 0.1.0, which means this is just the beginning. New features, improvements and fixes are already waiting backstage. <:headpat:1515979847577632808>\n\n"

    #         "Ready to start?\n\n"

    #         "<a:musicbeat:1515979901063401673> `/play <song name or YouTube link>`\n\n"

    #         "Let's make some noise together. <3 <a:dance3:1515984893857763388>\n\n"
            
    #         "- *Sona, your personal DJ* <:sona:1518503432087011389>"
    #     )

    # ==============================
    # END OF ANNOUNCEMENT BLOCK
    # ==============================


bot.run(TOKEN)