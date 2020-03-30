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
        '''
        This event only really cares about the bots own storage servers. 
        
        It sets up some basics for each emoji server. 

        There is a command to wait half a second between each command that talks to discord, 
        since discord can be a bit buggy if you send off a ton of edits and creates at once.
        '''

        # ===== If guild is not a storage guild, ignore it.
        if not guild.owner_id == self.bot.user.id:
            return 

        # ===== Wait a bit because we have to re-fetch the guild object.
        await asyncio.sleep(2.0)

        # ===== Refetch Guild because discord.py is shit.
        guild = discord.utils.get(self.bot.guilds, id=guild.id)

      # -------------------- Nuke Guild Defaults. --------------------
        # ----- Delete General Channels.
        for chl in guild.channels:
            await chl.delete()
            await asyncio.sleep(0.2)

        # ----- Delete Default Categories.
        for cat in guild.categories:
            await cat.delete()
            await asyncio.sleep(0.2)

        # ----- Create System Messages channel
        chl = await guild.create_text_channel(
            name=               'System Messages',
            reason=             'For system Messages.',
            overwrites =        {
                                    guild.default_role:     discord.PermissionOverwrite(      
                                        send_messages=False,        manage_webhooks=False,
                                        manage_permissions=False,   manage_channels=False,  create_instant_invite=False),
                                },
            topic=              'These are the people that joined this guild.'
            )

        # ----- Wait
        await asyncio.sleep(0.5)

        # ----- Fix Discords Bullshit Settings.
        await guild.edit(
            default_notifications=  discord.NotificationLevel.only_mentions,
            system_channel=         chl,
            reason=                 'Fix discords BS Settings.'
            )

        # ----- Wait
        await asyncio.sleep(0.5)


      # -------------------- Important Owner Stuff --------------------
        # ----- Get Bot Owner
        bot_owner = await self.bot._get_owner()

        # ----- Wait
        await asyncio.sleep(0.5)

        # ----- Create Bot Owner Role
        owner_role = await guild.create_role(
            name=               "Bot Owner",
            permissions=        discord.Permissions(administrator=True),
            reason=             "Bot owner role."
            )

        # ----- Wait
        await asyncio.sleep(0.5)
        
        # ----- Create Default text channel
        chl = await guild.create_text_channel(
            name=               'default',
            reason=             'discord.py is unreliable.',
            overwrites =        {
                                    guild.default_role:     discord.PermissionOverwrite(
                                        read_messages=False,        send_messages=False,    manage_webhooks=False,
                                        manage_permissions=False,   manage_channels=False,  create_instant_invite=False),
                                    guild.me:               discord.PermissionOverwrite(read_messages=True),
                                    owner_role:             discord.PermissionOverwrite(read_messages=True)
                                },
            topic=              'Do Not Delete or Rename This Channel'
            )

        # ----- Wait
        await asyncio.sleep(0.5)

        # ----- Create Perm invite for Bot Owner
        invite = await chl.create_invite(
            max_age=            0,
            unique=             True,
            reason=             "Bot Owner invite."
            )

        # ----- Wait
        await asyncio.sleep(0.5)

        # ----- Send Bot Owner the Invite
        await bot_owner.send(invite.url)

        # ----- Wait
        await asyncio.sleep(0.5)


      # -------------------- Bot Related Stuff. --------------------

        # ----- Make bot related category
        bot_cat = await guild.create_category(
            name=               'Emoji Bot Stuff',
            overwrites=         {
                                    guild.default_role:     discord.PermissionOverwrite(
                                        read_messages=False,        send_messages=False,    manage_webhooks=False,
                                        manage_permissions=False,   manage_channels=False,  create_instant_invite=False),
                                },
            reason=             'It is needed.'
        )

        # ----- Wait
        await asyncio.sleep(0.5)

        await bot_cat.edit(
            position=           0
        )

        # ----- Wait
        await asyncio.sleep(0.5)

        # ----- All Emotes
        await guild.create_text_channel(
            name=               '📖all_available_emojis',
            topic=              'Here is a list of all emojis the bot can access.',
            category=           bot_cat,
        )
        
        # ----- Wait
        await asyncio.sleep(0.5)

        # ----- Guild Emotes
        await guild.create_text_channel(
            name=               '🧾emojis_on_this_guild',
            topic=              'Here are all the emojis on this server.',
            category=           bot_cat,
        )
        
        # ----- Wait
        await asyncio.sleep(0.5)

        # ----- Suggestions.
        await guild.create_text_channel(
            name=               '💡suggestions',
            topic=              'Suggest more emojis.',
            slowmode_delay=     60,
            category=           bot_cat,
        )


        return 

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.bot.safe_print("Member Joined")

        # ====== Filter out the bot joining a guild
        if not member.guild.owner_id == self.bot.user.id:
            return 
        
        # ====== Filter out normies.
        if not member.id == self.bot.config.owner_id:
            return 

        self.bot.safe_print("Bot Owner Joined")

        # ====== Give Bot Owner Perms.
        owner_role = discord.utils.get(member.guild.roles, name='Bot Owner')

        # ----- Owner Role not Found
        if not owner_role:
            owner_role = await member.guild.create_role(
                name=       "Bot Owner",
                permissions=discord.Permissions(administrator=True),
                colour=     RANDOM_DISCORD_COLOUR(),
                hoist=      True,
                reason=     "Bot owner role."
            )

            await asyncio.sleep(1.0)

        # ----- Check and or Correct Owner Role Position
        if not owner_role.position == (len(member.guild.roles) - 1):
            await owner_role.edit(
                position =  (len(member.guild.roles) - 1),
                reason=     'Keep Owner Role on Top'
            )

            await asyncio.sleep(1.0)
        
        await member.add_roles(
            owner_role,
            reason=         'Give the Bot Owner their Role.'
            )

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        """
        before (Sequence[Emoji]) – A list of emojis before the update.
        after (Sequence[Emoji]) – A list of emojis after the update.
        """

        pass

    @commands.Cog.listener()
    async def on_message(self, msg):
        
        # ===== Ignore Bots
        if msg.author.bot:
            return

        # ===== Forcefully Ignore Webhooks
        if msg.webhook_id:
            return

        pattern = re.compile(r':(.*?):', re.DOTALL)
        msg_content = msg.content

        for et in set(pattern.findall(msg.content)):
            for e in msg.guild.emojis:
                
                found_emoji = None 
                
                if e.name == et:
                    found_emoji = e 
                    break

            if found_emoji is None:
                continue

            msg_content = msg_content.replace(f':{et}:', f'<{"a" if e.animated else ""}:{e.name}:{e.id}>')

        if msg_content == msg.content:
            return

        print(msg.content)
        print(msg.clean_content)

        await self.bot.execute_webhook2(
            channel=        msg.channel,
            content=        msg_content,
            username=       msg.author.display_name,
            avatar_url=     AVATAR_URL_AS(msg.author, format="png", size=128)
        )

        await msg.delete()


  # -------------------- Commands -------------------- 
    @commands.command(pass_context=True, hidden=False, name='createstorageguild', aliases=[])
    async def cmd_createstorageguild(self, ctx):
        await self.bot.create_storage_server()

        return

    @commands.command(pass_context=True, hidden=False, name='storage_inviteme', aliases=[])
    async def cmd_storage_inviteme(self, ctx):

        bot_owner = await self.bot._get_owner()

        for guild in self.bot.guilds:

            if guild.owner_id != self.bot.user.id:
                continue 
            
            default_channel = None 

            for chl in guild.channels:
                if chl.name == "default":
                    default_channel = chl
            
            if default_channel is None:
                default_channel = await guild.create_text_channel(
                    name='default',
                    reason='discord.py is unreliable.'
                )

                await asyncio.sleep(1)

            invite = await default_channel.create_invite(
                max_age=0,
                max_uses=1,
                unique=True,
                reason="Bot Owner invite."
            )

            await bot_owner.send(invite.url)

        return 
        

    @commands.command(pass_context=True, hidden=False, name='delete_storages', aliases=[])
    async def cmd_delete_storages(self, ctx):
        for guild in self.bot.guilds:

            if guild.owner_id != self.bot.user.id:
                continue 

            await guild.delete()
            await asyncio.sleep(0.5)

        await ctx.send("Done")

        return


def setup(bot):
    bot.add_cog(Test(bot))