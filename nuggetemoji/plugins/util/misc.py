"""
----~~~~~ NuggetBot ~~~~~----
Written By Calamity Lime#8500

Disclaimer
-----------
NuggetBots source code as been shared for the purposes of transparency on the FurSail discord server and educational purposes.
Running your own instance of this bot is not recommended.

FurSail Invite URL: http://discord.gg/QMEgfcg

Kind Regards
-Lime
"""

import os
import random
import discord
import asyncio
import colorsys
import datetime
from io import BytesIO
from typing import Union
from discord import User, Member


def RANDOM_DISCORD_COLOUR():
    choice = random.choice([1]*10 + [2]*20 + [3]*20)

    if choice == 1:
        values = [int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1)]
    elif choice == 2: 
        values = [int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), random.random(), 1)]
    else:
        values = [int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), random.random(), random.random())]

    color = discord.Color.from_rgb(*values)

    return color

def AVATAR_URL_AS(user, format=None, static_format='webp', size=256):
    if not isinstance(user, discord.abc.User):
        return 'https://cdn.discordapp.com/embed/avatars/0.png'

    if user.avatar is None:
        # Default is always blurple apparently
        #return user.default_avatar_url
        return 'https://cdn.discordapp.com/embed/avatars/{}.png'.format(user.default_avatar.value)

    format = format or 'png'

    return 'https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.{1}?size={2}'.format(user, format, size)

def GUILD_URL_AS(guild, format=None, static_format='webp', size=256):
    if not isinstance(guild, discord.Guild):
        return 'https://cdn.discordapp.com/embed/avatars/0.png'
    
    if format is None:
        format = 'gif' if guild.is_icon_animated() else static_format

    return 'https://cdn.discordapp.com/icons/{0.id}/{0.icon}.{1}?size={2}'.format(guild, format, size)


# -------------------- ENGLISH FTW --------------------

RANDOM_DISCORD_COLOR = RANDOM_DISCORD_COLOUR