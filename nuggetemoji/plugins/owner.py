import sys
import discord
import asyncio

from typing import Union
from functools import partial
from discord.ext import commands
from .util import checks, cogset
from .util.misc import RANDOM_DISCORD_COLOUR, AVATAR_URL_AS, GUILD_URL_AS

from nuggetemoji.util.exceptions import RestartSignal, TerminateSignal





class Owner(commands.Cog):
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
        
        print('Ignoring exception in {}'.format(ctx.invoked_with), file=sys.stderr)
        print(error)


  # -------------------- COMMANDS -------------------- 
    @checks.BOT_OWNER()
    @commands.command(pass_context=True, hidden=False, name='reboot', aliases=['restart'])
    async def cmd_reboot(self, ctx):
        """
        [Disabled command]
        """

        raise RestartSignal
    
    @checks.BOT_OWNER()
    @commands.command(pass_context=True, hidden=False, name='shutdown', aliases=['logout'])
    async def cmd_shutdown(self, ctx):
        """
        [Disabled command]
        """

        raise TerminateSignal

    @cmd_shutdown.error
    @cmd_reboot.error
    async def _reboot_error(self, ctx, error):
        raise error.original



def setup(bot):
    bot.add_cog(Owner(bot))