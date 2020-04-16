import sys
import discord
import asyncio
import datetime
from typing import Union

from discord.ext import commands
from .util import checks

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

  # -------------------- local Cog Events -------------------- 

    @asyncio.coroutine
    async def cog_before_invoke(self, ctx):
        await ctx.channel.trigger_typing()

    @asyncio.coroutine
    async def cog_after_invoke(self, ctx):
        if self.bot.config.delete_invoking:
            try:
                await ctx.message.delete()
            except discord.errors.NotFound:
                pass 
            except discord.errors.Forbidden:
                pass

    @asyncio.coroutine
    async def cog_command_error(self, ctx, error):
        if self.bot.config.delete_invoking:
            try:
                await ctx.message.delete()
            except discord.errors.NotFound:
                pass 
            except discord.errors.Forbidden:
                pass
        
        print('Ignoring exception in {}'.format(ctx.invoked_with), file=sys.stderr)
        print(error)

  # -------------------- LISTENERS -------------------- 
    @commands.Cog.listener()
    async def on_ready(self):
        pass

def setup(bot):
    bot.add_cog(Help(bot))