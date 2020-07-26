import sys
import psutil
import discord
import asyncio
import pathlib
import datetime
import platform

from typing import Union
from functools import partial
from discord.ext import commands
from .util import checks, cogset
from .util.misc import RANDOM_DISCORD_COLOUR, AVATAR_URL_AS, GUILD_URL_AS

from nuggetemoji.util.exceptions import RestartSignal, TerminateSignal





class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

  # -------------------- STATIC METHODS --------------------
    @staticmethod
    async def oneline_valid(content):
        try:
            args = content.split(" ")
            if len(args) > 1:
                return False 

            return True

        except (IndexError, ValueError):
            return False

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
    @commands.command(pass_context=True, hidden=False, name='hoststats', aliases=[])
    async def cmd_hoststats(self, ctx):
        """
        [Bot Owner] Returns current system utilzation of the bots host.
        """

        valid = await self.oneline_valid(ctx.message.content)
        if not valid:
            return

        def MBorGB(val):
            ret = val/1073741824

            if ret < 1:
                ret = "{0:.2f} MB".format((val/1048576))
                return ret 

            ret = "{0:.2f} GB".format(ret)
            return ret

        # ===== CPU INFORMATION
        cpu_freq = psutil.cpu_freq()

        # ===== PHYSICAL RAM
        mem = psutil.virtual_memory()

        # ===== DISK DRIVE SPACE    
        d = psutil.disk_usage(pathlib.Path.cwd().__str__())

        # ===== UPTIME
        updelta = datetime.datetime.utcnow() - self.bot.start_timestamp

        seconds = updelta.seconds

        hours = int(seconds / 3600)
        if hours > 1:
            seconds = hours * 3600

        minutes = int(seconds / 60)
        if minutes > 1:
            seconds = minutes * 60
        

        embed = discord.Embed(  title=      "Host System Stats",
                                description="",
                                colour=     RANDOM_DISCORD_COLOR(),
                                timestamp=  datetime.datetime.utcnow(),
                                type=       "rich"
                                )


        embed.add_field(
            name=   "CPU:",
            value=  f"> **Cores:** {psutil.cpu_count(logical=False)} ({psutil.cpu_count(logical=True)})\n"
                    f"> **Architecture:** {platform.machine()}\n"
                    f"> **Affinity:** {len(psutil.Process().cpu_affinity())}\n"
                    f"> **Useage:** {psutil.cpu_percent()}%\n"
                    f"> **Freq:** {cpu_freq[0]} Mhz",
            inline= True
            )
        
        embed.add_field(
            name=   "Memory:",
            value=  f"> **Total:** {MBorGB(mem[0])}\n"
                    f"> **Free:** {MBorGB(mem[1])}\n"
                    f"> **Used:** {mem[2]}%",
            inline= True
            )
        
        embed.add_field(
            name=   "Storage:",
            value=  f"> **Total:** {MBorGB(d[0])}\n"
                    f"> **Free:** {MBorGB(d[2])}\n"
                    f"> **Used:** {d[3]}%",
            inline= True
            )

        embed.add_field(
            name=   "Network:",
            value=  "> **Useage:**\n"
                    f"> - Send: {MBorGB(psutil.net_io_counters().bytes_sent)}"
                    f"> - Recv: {MBorGB(psutil.net_io_counters().bytes_recv)}",
            inline= True
            )

        embed.add_field(
            name=   "Python:",
            value=  f"> **Version:** {platform.python_version()}\n"
                    f"> **Discord.py** {discord.__version__}\n"
                    f"> **Bits:** {platform.architecture()[0]}",
            inline= True
            )

        embed.add_field(
            name=   "Bot Uptime:",
            value=  f"> **Launched:** {self.bot.start_timestamp.strftime('%b %d, %Y')}\n"
                    f"> **Time:** days:{updelta.days}, hours:{hours}, minutes:{minutes}, seconds:{seconds}\n",
            inline= True
            )

        embed.add_field(
            name=       "Process",
            value=      f"> **Memory:** {MBorGB(psutil.Process().memory_info().rss)}\n"
                        f"> **CPU:**    {psutil.Process().cpu_percent(interval=2)}%\n"
                        f"> **Threads:**{psutil.Process().num_threads()}",
            inline= True
            )

        embed.set_author(
            name=   f"{self.bot.user.name}#{self.bot.user.discriminator}",
            icon_url=AVATAR_URL_AS(self.bot.user)
            )
        
        embed.set_thumbnail(
            url=        AVATAR_URL_AS(user=self.bot.user, format=None, size=512)
            )

        await ctx.channel.send(embed = embed)
        return


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