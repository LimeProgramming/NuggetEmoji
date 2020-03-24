# ==================== Imports ====================
import discord
import datetime
import random
import asyncio
import colorsys


# ==================== Owner Commands ====================
async def ownerRestart(msg):

    embed = discord.Embed(  
        description=    "Restarting 👋",
        colour=         0x6BB281,
        timestamp=      datetime.datetime.utcnow(),
        type=           "rich"
        )

    embed.set_footer(       
        icon_url=       GUILD_URL_AS(msg.guild), 
        text=           msg.guild.name
        )

    embed.set_author(       
        name=           "Owner Command",
        icon_url=       AVATAR_URL_AS(user=msg.author)
        )

    return embed 

async def ownerShutdown(msg):
    embed = discord.Embed(  
        description=    "Shutting Down 👋",
        colour=         0x6BB281,
        timestamp=      datetime.datetime.utcnow(),
        type=           "rich"
        )

    embed.set_footer(
        icon_url=       GUILD_URL_AS(msg.guild), 
        text=           msg.guild.name
        )

    embed.set_author(
        name=           "Owner Command",
        icon_url=       AVATAR_URL_AS(user=msg.author)
        )

    return embed


# ==================== Functions ====================
def AVATAR_URL_AS(user, format=None, static_format='webp', size=256):
    if not isinstance(user, discord.abc.User):
        return 'https://cdn.discordapp.com/embed/avatars/0.png'

    if user.avatar is None:
        # Default is always blurple apparently
        return 'https://cdn.discordapp.com/embed/avatars/{}.png'.format(user.default_avatar.value)

    format = format or 'png'

    return 'https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.{1}?size={2}'.format(user, format, size)


def GUILD_URL_AS(guild, format=None, static_format='webp', size=256):
    if not isinstance(guild, discord.Guild):
        return 'https://cdn.discordapp.com/embed/avatars/0.png'
    
    if format is None:
        format = 'gif' if guild.is_icon_animated() else static_format

    return 'https://cdn.discordapp.com/icons/{0.id}/{0.icon}.{1}?size={2}'.format(guild, format, size)

def random_embed_color():
    choice = random.choice([1]*10 + [2]*20 + [3]*20)

    if choice == 1:
        values = [int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1)]
    elif choice == 2: 
        values = [int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), random.random(), 1)]
    else:
        values = [int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), random.random(), random.random())]

    color = discord.Color.from_rgb(*values)

    return color