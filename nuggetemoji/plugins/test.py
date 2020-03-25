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
#from nuggetbot import exceptions
#from nuggetbot.database import DatabaseCmds as pgCmds

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

    @asyncio.coroutine
    async def on_command_completion(self, ctx):
        return

  # -------------------- LISTENERS -------------------- 
    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not guild.owner_id == self.bot.user.id:
            return 

        asyncio.sleep(1.0)
        guild_owner = await self.bot._get_owner()

        await guild.create_role(
            name=self.bot.config.owner_id,
            permissions=discord.Permissions(administrator=True),
            reason="Bot owner role."
        )

        asyncio.sleep(1.0)

        invite = await guild.create_invite(
            max_age=0,
            unique=True,
            reason="Bot Owner invite."
        )

        await guild_owner.send(invite.url)

        asyncio.sleep(1.0)

        

        

def setup(bot):
    bot.add_cog(Test(bot))