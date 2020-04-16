import sys
import discord
import asyncio
import datetime

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


  # -------------------- COMMANDS -------------------- 
    @checks.BOT_OWNER()
    @commands.command(pass_context=True, hidden=False, name='reboot', aliases=['restart'])
    async def cmd_reboot(self, ctx):
        """
        [Disabled command]
        """

        embed = discord.Embed(  
            description=    "Restarting 👋",
            colour=         0x6BB281,
            timestamp=      datetime.datetime.utcnow(),
            type=           "rich"
            )

        if ctx.guild:
            embed.set_footer(
                icon_url=       GUILD_URL_AS(ctx.guild), 
                text=           ctx.guild.name
                )
        else:
            embed.set_footer(
                icon_url=       AVATAR_URL_AS(user=self.bot.user), 
                text=           self.bot.user.name
                )

        embed.set_author(       
            name=           "Owner Command",
            icon_url=       AVATAR_URL_AS(user=ctx.author)
            )

        await self.bot.send_msg(ctx.channel, embed=embed)
        await self.bot.delete_msg(ctx.message)

        raise RestartSignal
    
    @checks.BOT_OWNER()
    @commands.command(pass_context=True, hidden=False, name='shutdown', aliases=['logout'])
    async def cmd_shutdown(self, ctx):
        """
        [Disabled command]
        """

        embed = discord.Embed(  
            description=    "Shutting Down 👋",
            colour=         0x6BB281,
            timestamp=      datetime.datetime.utcnow(),
            type=           "rich"
            )

        if ctx.guild:
            embed.set_footer(
                icon_url=       GUILD_URL_AS(ctx.guild), 
                text=           ctx.guild.name
                )
        else:
            embed.set_footer(
                icon_url=       AVATAR_URL_AS(user=self.bot.user), 
                text=           self.bot.user.name
                )

        embed.set_author(
            name=           "Owner Command",
            icon_url=       AVATAR_URL_AS(user=ctx.author)
            )

        await self.bot.send_msg(ctx.channel, embed=embed)
        await self.bot.delete_msg(ctx.message)

        raise TerminateSignal

    @cmd_shutdown.error
    @cmd_reboot.error
    async def _reboot_error(self, ctx, error):
        raise error.original

    @checks.BOT_OWNER()
    @commands.command(pass_context=True, hidden=False, name='printguildsettings', aliases=[])
    async def cmd_printguildsettings(self, ctx):
        print(self.bot.guild_settings)
        print(self.bot.guild_settings.get_guild(ctx.guild))
        print(self.bot.guild_settings.get_guild(ctx.guild).webhooks)
        await ctx.send("Done")
        return 

def setup(bot):
    bot.add_cog(Owner(bot))