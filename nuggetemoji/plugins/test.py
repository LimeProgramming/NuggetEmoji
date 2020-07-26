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
from .util.unicode_links import EMOJI_UNICODE_LINKS, EMOJI_UNICODE_LINKS_96
from .util.misc import RANDOM_DISCORD_COLOUR, AVATAR_URL_AS, GUILD_URL_AS
#from nuggetbot import exceptions
#from nuggetbot.database import DatabaseCmds as pgCmds
from nuggetemoji.util.allowed_mentions import AllowedMentions
from nuggetemoji.util.exceptions import RestartSignal, TerminateSignal

_EMOJI_REGEXP = None

class Test(commands.Cog):
    """Poll voting system."""

    def __init__(self, bot):
        self.bot = bot
        self.db = None

  # -------------------- local Cog Events -------------------- 

    @asyncio.coroutine
    async def cog_before_invoke(self, ctx):
        pass

        #await ctx.channel.trigger_typing()

    @asyncio.coroutine
    async def cog_after_invoke(self, ctx):
        if self.bot.config.delete_invoking:
            try:
                await ctx.message.delete()
            except (discord.errors.NotFound, discord.errors.Forbidden):
                pass 

    @asyncio.coroutine
    async def cog_command_error(self, ctx, error):

        print('Ignoring exception in {}'.format(ctx.invoked_with), file=sys.stderr)
        print(error)

        if self.bot.config.delete_invoking:
            try:
                await ctx.message.delete()
            except (discord.errors.NotFound, discord.errors.Forbidden):
                pass 


  # -------------------- Listeners -------------------- 

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
                msg_content = msg_content.replace(f':{et}:', f'[](https://cdn.discordapp.com/emojis/{e.id}.{"gif" if e.animated else "png"}?size=128?v=1 )')

        # ===== Exit if no changes were made.
        if msg_content == msg.content: return

        # ===== Get guild settings
        guild_setting = self.bot.guild_settings.get_guild(msg.guild)
    
        if guild_setting.allowed_roles:
            if not bool(set(guild_setting.allowed_roles).intersection(set([i.id for i in msg.author.roles]))):
                return

        # ===== Sort out mentions
        allowed_mentions = None 

        if guild_setting.allow_mentions and guild_setting.allow_everyone:

            if msg.channel.permissions_for(msg.author).mention_everyone:
                allowed_mentions = AllowedMentions(everyone=True, roles=True, users=True)

            allowed_mentions = AllowedMentions(everyone=False, roles=True, users=True)
        
        elif guild_setting.allow_mentions:
            allowed_mentions = AllowedMentions(everyone=False, roles=True, users=True)

        elif guild_setting.allow_everyone:
            if msg.channel.permissions_for(msg.author).mention_everyone:
                allowed_mentions = AllowedMentions(everyone=True, roles=False, users=False)

        stripper = re.compile(r'[:\s+][\s+:]', re.UNICODE)
        msg_content = stripper.sub('', msg_content)

        await self.bot.send_emote(
            dest=               msg.channel,
            content=            msg_content,
            msg_author=         msg.author,
            allowed_mentions=   allowed_mentions
            )

        await self.bot.delete_msg(msg, quiet=True)
        return


  # -------------------- Cog Commands -------------------- 

    @commands.command(pass_context=True, hidden=False, name='large', aliases=[])
    async def large(self, ctx, emoji):

      # ---------- Get guild settings ----------
        guild_setting = self.bot.guild_settings.get_guild(ctx.guild)

        if guild_setting.allowed_roles:
            if not bool(set(guild_setting.allowed_roles).intersection(set([i.id for i in ctx.author.roles]))):
                return #exit

      # ---------- Get emoji regex pattern ----------
        epattern = await self.get_isemoji_regex()

        try:
            match = epattern.match(emoji)[0]
        except TypeError:
            # === Will throw if no emoji as been supplied
            pass

      # ---------- Find emoji link ----------
        link = EMOJI_UNICODE_LINKS_96.get(match, None)
        #link = EMOJI_UNICODE_LINKS.get(emoji, None)
        
        # ===== If emoji not found
        if link is None: 
            # === Will throw if no link has been found
            return 

        msg_content = f'[]({link}?v=1 )'

      # ---------- Sort out mentions ----------
        allowed_mentions = None 

        if guild_setting.allow_mentions and guild_setting.allow_everyone:

            if ctx.channel.permissions_for(ctx.author).mention_everyone:
                allowed_mentions = AllowedMentions(everyone=True, roles=True, users=True)

            allowed_mentions = AllowedMentions(everyone=False, roles=True, users=True)
        
        elif guild_setting.allow_mentions:
            allowed_mentions = AllowedMentions(everyone=False, roles=True, users=True)

        elif guild_setting.allow_everyone:
            if ctx.channel.permissions_for(ctx.author).mention_everyone:
                allowed_mentions = AllowedMentions(everyone=True, roles=False, users=False)
        
      # ---------- Send emote ----------
        await self.bot.send_emote(
            dest=               ctx.channel,
            content=            msg_content,
            msg_author=         ctx.author,
            allowed_mentions=   allowed_mentions
            )


  # -------------------- Functions -------------------- 

    async def get_isemoji_regex(self):
        global _EMOJI_REGEXP
        
        # Build emoji regexp once
        if _EMOJI_REGEXP is None:
            # Sort emojis by length to make sure multi-character emojis are
            # matched first
            emojis = sorted(EMOJI_UNICODE_LINKS_96.keys(), key=len, reverse=True)
            #emojis = sorted(EMOJI_UNICODE_LINKS.keys(), key=len, reverse=True)
            pattern = u'(' + u'|'.join(re.escape(u) for u in emojis) + u')'
            _EMOJI_REGEXP = re.compile(pattern)
        
        return _EMOJI_REGEXP


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