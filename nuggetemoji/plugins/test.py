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
        
        # ===== Ignore DMs
        if not msg.guild:
            return

        # ===== Ignore Bots
        if msg.author.bot:
            return

        # ===== Forcefully Ignore Webhooks
        if msg.webhook_id:
            return

        pattern = re.compile(r':([^\s-].*?):', re.DOTALL)
        msg_content = msg.content

        for et in set(pattern.findall(msg.content)):
            for e in msg.guild.emojis:
                
                found_emoji = None 

                # = Skip static emotes since everyone can use those anyway.
                if not e.animated:
                    continue 
                
                # = If emoji name is a match, note it and break inner loop 
                if e.name == et:
                    found_emoji = e 
                    break
            
            # === If inner loop failed to find emoji, skip to next find.
            if found_emoji is None:
                continue
            
            # === Replace sent emote with emote id.
            msg_content = msg_content.replace(f':{et}:', f'<{"a" if e.animated else ""}:{e.name}:{e.id}>')
        
        # ===== Exit if no changes were made.
        if msg_content == msg.content:
            return

        # ===== Checked allowed roles in the Guild
        allowed_roles = await self.bot.test_db.get_guild_allowed_roles(msg.guild)

        if allowed_roles:
            if not bool(set(allowed_roles).intersection(set([i.id for i in msg.author.roles]))):
                return

        stripper = re.compile(r'[:\s+][\s+:]', re.UNICODE)
        msg_content = stripper.sub('', msg_content)

        await self.bot.execute_webhook3(
            channel=        msg.channel,
            content=        msg_content,
            username=       msg.author.display_name,
            avatar_url=     AVATAR_URL_AS(msg.author, format="png", size=128)
        )

        await msg.delete()





def setup(bot):
    bot.add_cog(Test(bot))