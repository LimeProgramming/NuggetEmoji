import sys
import discord
import asyncio
import datetime

from typing import Union
from functools import partial
from discord.ext import commands
from .util import checks, cogset
from .util.misc import RANDOM_DISCORD_COLOUR, AVATAR_URL_AS, GUILD_URL_AS

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


  # -------------------- local Cog Events -------------------- 
  
    @asyncio.coroutine
    async def cog_before_invoke(self, ctx):
        await ctx.channel.trigger_typing()

    @asyncio.coroutine
    async def cog_after_invoke(self, ctx):
        if self.bot.confing.delete_invoking:
            try:
                await ctx.delete()
            except discord.errors.NotFound:
                pass 

    @asyncio.coroutine
    async def cog_command_error(self, ctx, error):
        if self.bot.confing.delete_invoking:
            try:
                await ctx.delete()
            except discord.errors.NotFound:
                pass 

  # -------------------- Cog Listeners -------------------- 

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        pass
        #if isinstance(error, CheckEXC.CustomCheckFailure):
        #    await ctx.send(embed=error.embed, delete_after=30)
        #    return


  # -------------------- Cog Commands -------------------- 
    @checks.HAS_PERMISSIONS(administrator=True)
    @commands.command(pass_context=True, hidden=False, name='admintest', aliases=[])
    async def cmd_admintest(self, ctx):
        print("am I working anyway?")
        return

def setup(bot):
    bot.add_cog(Admin(bot))