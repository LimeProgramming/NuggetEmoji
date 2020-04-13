import sys
import json
import discord
import asyncio
import datetime

from typing import Union
from functools import partial
from discord.ext import commands
from .util import checks, cogset
from .util.misc import RANDOM_DISCORD_COLOUR, AVATAR_URL_AS, GUILD_URL_AS
from nuggetemoji.util.allowed_mentions import AllowedMentions

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


  # -------------------- local Cog Events -------------------- 

    @asyncio.coroutine
    async def cog_before_invoke(self, ctx):
        #if "sends webhook" in (ctx.command.help).lower():
        #    return

        await ctx.channel.trigger_typing()

    @asyncio.coroutine
    async def cog_after_invoke(self, ctx):
        if self.bot.config.delete_invoking:
            try:
                await ctx.message.delete()
            except discord.errors.NotFound:
                pass 

    @asyncio.coroutine
    async def cog_command_error(self, ctx, error):
        if self.bot.config.delete_invoking:
            try:
                await ctx.message.delete()
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
    
    @checks.GUILD_ONLY()
    @checks.HAS_PERMISSIONS(administrator=True)
    @commands.command(pass_context=True, hidden=False, name='allowrole', aliases=[])
    async def cmd_allowrole(self, ctx, role : discord.Role):

        if not role in ctx.message.guild.roles:
            await ctx.send(f"The role {role.name} is not in this guild.")
            return 

        ret = await self.bot.db.add_guild_allowed_role(role, role.guild)

        await ret

        return

    @checks.GUILD_ONLY()
    @checks.HAS_PERMISSIONS(administrator=True)
    @commands.command(pass_context=True, hidden=False, name='getallowedroles', aliases=[])
    async def cmd_getallowedroles(self, ctx):
        """
        Gets and returns a list of roles whom are allowed to post animated emojis with the aid of this bot.

        Sends Webhook to avoid pinging the roles.
        """

        a_roles = await self.bot.db.get_guild_allowed_roles(ctx.guild)

        if not a_roles:
            await ctx.send("No roles are set to be allowed ro use animated emotes.\nTherefore\n\tEveryone is allowed to use animated emotes.")
            return 

        msg_content = "The following roles are allowed to use animated emotes.\n"

        msg_content = msg_content + '\n'.join([':white_small_square:'+ f'<@&{i}>' for i in a_roles])

        await self.bot.send_msg2(ctx, content=msg_content, allowed_mentions=AllowedMentions(roles=False))
        #await self.bot.execute_webhook3(
        #    channel=        ctx.channel,
        #    content=        msg_content,
        #    username=       self.bot.user.name,
        #    avatar_url=     AVATAR_URL_AS(self.bot.user, format="png", size=128)
        #)

        return 


    async def cmd_checkemotes(self, ctx):
        try:
            with open('data/stock.json', 'w') as s:
                unicodeEmotes = json.load(s)
        except FileNotFoundError:
            unicodeEmotes = []



def setup(bot):
    bot.add_cog(Admin(bot))