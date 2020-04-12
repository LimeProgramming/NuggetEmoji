import os
import re
import sys
import random
import asyncpg
import discord
import asyncio

from io import BytesIO
from typing import Union
from pathlib import Path
from functools import partial
from discord.ext import commands

from .util import checks, cogset
from .util.misc import RANDOM_DISCORD_COLOUR, AVATAR_URL_AS, GUILD_URL_AS
#from nuggetbot import exceptions
#from nuggetbot.database import DatabaseCmds as pgCmds

from nuggetemoji.util.exceptions import RestartSignal, TerminateSignal

import dblogin 

class Test(commands.Cog):
    """Poll voting system."""

    def __init__(self, bot):
        self.bot = bot
        self.db = None

  # -------------------- LOCAL COG STUFF -------------------- 
    @asyncio.coroutine
    async def cog_command_error(self, ctx, error):
        return
        print('Ignoring exception in {}'.format(ctx.invoked_with), file=sys.stderr)
        print(error)
        return

    @asyncio.coroutine
    async def on_command_completion(self, ctx):
        return

  # -------------------- LISTENERS -------------------- 
    @commands.Cog.listener()
    async def on_ready(self):
        pass





    @commands.Cog.listener()
    async def on_message(self, msg):
        
        # ===== Ignore DMs, Bots, Webhooks
        if not msg.guild or msg.author.bot or msg.webhook_id: return

        # ===== Variable Setup
        pattern = re.compile(r':([^\s-].*?):', re.DOTALL)
        msg_content = msg.content

        # ===== Loop all emojis found
        for et in set(pattern.findall(msg.content)):
            
            ets = et.split('.')

            # === If normal emote is sent
            if len(ets) == 1:
                # = Get emote
                e = getEmoji(msg.guild.emojis, name=et, animated=True)

                # = If no emote found, skip
                if e is None: continue
                
                # = Replace sent emote with emote id.
                msg_content = msg_content.replace(f':{et}:', f'<{"a" if e.animated else ""}:{e.name}:{e.id}>')

            # === If large emote is wanted
            elif len(ets) == 2 and ets[0].lower() == "large":
                # = Get emote
                e = getEmoji(msg.guild.emojis, name=ets[1])

                # = If no emote found, skip
                if e is None: continue

                # = Replace sent emote with url link.
                msg_content = msg_content.replace(f':{et}:', f'[](https://cdn.discordapp.com/emojis/{e.id}.{"gif" if e.animated else "webp"}?size=128?v=1 )')

        # ===== Exit if no changes were made.
        if msg_content == msg.content: return

        # ===== Checked allowed roles in the Guild
        allowed_roles = await self.bot.db.get_guild_allowed_roles(msg.guild)

        if allowed_roles:
            if not bool(set(allowed_roles).intersection(set([i.id for i in msg.author.roles]))):
                return

        stripper = re.compile(r'[:\s+][\s+:]', re.UNICODE)
        msg_content = stripper.sub('', msg_content)

        await self.bot.execute_webhook3(
            dest=           msg.channel,
            content=        msg_content,
            username=       msg.author.display_name,
            avatar_url=     AVATAR_URL_AS(msg.author, format="png", size=128)
        )

        await msg.delete()



def getEmoji(emojis, name, animated=False):
    '''
    This is just a bit faster than discord.utils.get for getting emojis.
    '''

    for e in emojis:
        if animated and not e.animated:
            continue 

        if e.name == name:
            return e

    return None 

def setup(bot):
    bot.add_cog(Test(bot))