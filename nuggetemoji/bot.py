import re
import sys
import json
import dblogin
import asyncio
import aiohttp
import discord
import asyncpg
import logging
import pathlib
import datetime
import traceback
from typing import Union
from discord.ext import commands
from collections.abc import Iterable


from .config import Config
from .util import fake_objects as FakeOBJS

plugins = (
)

class NuggetEmoji(commands.Bot):

    RafEntryActive = False
    RafDatetime = {}
    reactionmsgs = ""

# ======================================== Bot init Setup ========================================
    def __init__(self):
        NuggetEmoji.bot = self
        self.config = Config()
        self.init_ok = True
        self.exit_signal = None

      # ---------- Store startup timestamp ----------
        self.start_timestamp = datetime.datetime.utcnow()

      # -------------------- Load in the Cogs --------------------
        for plugin in plugins:
            try:
                self.load_extension(plugin[0])
                self.safe_print(f"[Log] Loaded COG {plugin[1]}")
                
            except discord.ext.commands.ExtensionNotFound:
                print(f"Extention not found. {plugin}")

            except discord.ext.commands.ExtensionAlreadyLoaded:
                print(f"Extention already loaded, {plugin}.")

            except discord.ext.commands.NoEntryPointError:
                print(f"The extension does not have a setup function, {plugin}.")

            except discord.ext.commands.ExtensionFailed:
                print(f"The extension or its setup function had an execution error, {plugin}.")

            except Exception as e:
                print(e)
                print(f'Failed to load extension {plugin}.', file=sys.stderr) 

# ======================================== Custom Bot Class Functions ========================================
  # -------------------- Safe Send/Delete Messages --------------------

    @asyncio.coroutine
    async def send_msg(self, dest:Union[discord.TextChannel, discord.Message, discord.ext.commands.Context], *, content=None, embed=None, tts=False, expire_in=None, also_delete:discord.Message =None, quiet=True):
        '''
        Parameters
        ------------
        dest Union[:class:`discord.TextChannel`, :class:`discord.Message`, :class:`discord.Context`]
            Where to send the message to. If message or context is provided message will be sent to the same channel they are located.
        content :class:`str`
            The content of the message to send.
        embed :class:`discord.Embed`
            The rich embed for the content.
        tts :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        expire_in :class:`float`
            If provided, dictates how long the message should exist before being deleted
        also_delete :class:`discord.Message`
            Another message to also delete (typically invoking message), also affected by expire_in
        quiet :class:`bool`
            If True errors are not reported.

        Returns
        --------
        :class:`~discord.Message`
            The message that was sent.
        '''
        # ===== IF DESTINATION IS A MESSAGE
        if isinstance(dest, discord.Message):
            dest = dest.channel 

        msg = None
        try:
            msg = await dest.send(content=content, embed=embed, tts=tts, delete_after=expire_in)

            if also_delete and isinstance(also_delete, discord.Message):
                asyncio.ensure_future(self.__del_msg_later(also_delete, expire_in))

        except discord.Forbidden:
            if not quiet:
                self.safe_print("[Warning] Cannot send message to {dest.name}, no permission")

        except discord.NotFound:
            if not quiet:
                self.safe_print("[Warning] Cannot send message to {dest.name}, invalid channel?")

        return msg

    @asyncio.coroutine
    async def send_msg_chid(self, ch_id:Union[int, discord.Object], *, content:str = None, embed:discord.Embed = None, tts=False, expire_in:int = 0, also_delete:Union[discord.Message, discord.ext.commands.Context] = None, quiet=True, guild_id=None):
        '''
        Alt version of safe send message where messages can be send using channel id. Saves getting the channel from discord API.
        Made for sending to channels entered into the config.py. Also handles the exceptions to the best of it's ability.
        Must provide either embed or content.

        Parameters
        ------------
        ch_id Union[:class:`int`, :class:`discord.Object`]        
            Channel id of the destination, can be a private channel. 
            Discord.Object is supported for compatability 
        content :class:`str`           
            Text content which will be sent.
        embed :class:`discord.Embed` 
            Discord Embed object.
        tts :class:`boolean`         
            Enable text to speech or not.
        expire_in :class:`int`        
            Number of seconds before deleting the returned message
        also_delete Union[:class:`discord.Message`, :class:`discord.Context`]
            Another message to delete after time set with expire_in
        
        Returns
        --------
        :class:`~discord.Message`
            The message that was sent.

        '''
        
        # ===== COMPATABILITY REASONS
        if isinstance(ch_id, discord.Object):
            ch_id = ch_id.id 

        # ===== ENTURE CONTENT IS A STRING OR NONE
        content = str(content) if content is not None else None
        
        # ===== SERIALIZE EMBEDS
        if embed is not None:
            embed = embed.to_dict()

        msg = None

        try:
            msg = await self.bot.http.send_message(ch_id, content=content, embed=embed, tts=tts)

            fakemsg = FakeOBJS.FakeMsg1(msg, guild_id)

            # === SCHEDULE SENT MESSAGE FOR DELETION
            if expire_in:
                asyncio.ensure_future(self.delete_msg_id(fakemsg.id, fakemsg.channel.id, delay=expire_in))

            # === DELETE ADDITIONAL MESSAGE IF APPLICABLE
            if also_delete:
                asyncio.ensure_future(self.delete_msg(also_delete, delay=expire_in))

        except discord.Forbidden:
            if not quiet:
                self.safe_print(f"[Error] [new_members] Unable to send to channel {ch_id} due to lack of permissions.")

        except discord.NotFound:
            if not quiet:
                self.safe_print(f"[Error] [new_members] Cannot send message to channel {ch_id}, invalid channel?")

        return fakemsg

    @asyncio.coroutine
    async def delete_msg(self, message:discord.Message, reason:str = None, *, delay:float = None, quiet=False):
        """
        Messages to be deleted are routed though here to handle the exceptions. 
        Unlike message.delete() this function supports an audit log reason.

        Parameters
        ------------
        message :class:`discord.Message`
            Message to be deleted.
        reason :class:`str`
            Audit Log reason for deleteing the message
        delay: Optional[:class:`float`]
            If provided, the number of seconds to wait in the background before deleting the message.
        quiet :class:`bool`
            If True errors are not reported.
        """

        try:
            if delay is not None:

                async def delete():
                    await asyncio.sleep(delay, loop=message._state.loop)
                    await self.bot.http.delete_message(message.channel.id, message.id, reason=reason)

                asyncio.ensure_future(delete(), loop=message._state.loop)

            else:
                await self.bot.http.delete_message(message.channel.id, message.id, reason=reason)
            
        except discord.errors.Forbidden:
            if not quiet:
                self.safe_print(f"[Warning] Cannot delete message \"{message.clean_content}\", no permission")

        except discord.errors.NotFound:
            if not quiet:
                self.safe_print(f"[Warning] Cannot delete message \"{message.clean_content}\", message not found")

        except discord.errors.HTTPException:
            if not quiet:
                self.safe_print(f"[Warning] Cannot delete message \"{message.clean_content}\", generic error.")
            
        return
    
    @asyncio.coroutine
    async def delete_msg_id(self, message:int, channel:int, reason:str = None, *, delay:float = None, quiet=False):
        """
        Messages to be deleted are routed though here to handle the exceptions.
        This deletes using bot.http functions to bypass having to find each message before deleting it.

        Parameters
        ------------
        message :class:`int`
            Message ID of message to be deleted.
        channel :class:`int`
            Channel ID of channel the message was posted in.
        reason Optional[:class:`str`]
            Reason for message being deleted
        delay Optional[:class:`float`]
            If provided, the number of seconds to wait in the background before deleting the message.
        quiet Optional[:class:`bool`]
            If True errors are not reported.
        """
        
        try:
            if delay is not None:

                async def delete():
                    await asyncio.sleep(delay, loop=self.loop)
                    await self.bot.http.delete_message(channel_id=channel, message_id=message, reason=reason)

                asyncio.ensure_future(delete(), loop=self.loop)

            else:
                await self.bot.http.delete_message(channel_id=channel, message_id=message, reason=reason)

        except discord.errors.Forbidden:
            if not quiet:
                self.safe_print(f"[Warning] Cannot delete message \"{message}\", no permission")

        except discord.errors.NotFound:
            if not quiet:
                self.safe_print(f"[Warning] Cannot delete message \"{message}\", message not found")

        except discord.errors.HTTPException:
            if not quiet:
                self.safe_print(f"[Warning] Cannot delete message \"{message}\", generic error.")
        return

    @asyncio.coroutine
    async def delete_msgs_id(self, messages:list, channel:int, reason:str = None, quiet=False):
        """
        Bulk message deletes are routed though here to handle the exceptions.
        This deletes using bot.http functions to bypass having to find each message and channel before deleting.
        Also safely handles message id lists greater than 100 messages 
        
        Parameters
        ------------
        messages List[:class:`int`]
            List of message ID's to be deleted.
        channel :class:`int`
            Channel ID of channel the messages are posted in.
        reason Optional[:class:`str`]
            Reason for messages being deleted
        quiet Optional[:class:`bool`]
            If True errors are not reported.

        """

        # ===== DO NOTHING IF USER IS BEING SILLY
        if len(messages) == 0:
            return

        # ===== IF LENTH MESSAGES IS 1, DELETE IT NORMALLY.
        if len(messages) == 1:
            await self.delete_msg_id(messages[0], channel, reason, quiet=quiet)
            return

        # ===== SPLIT MESSAGES LIST TO ENSURE NUM IS 100 OR LESS, DISCORD API LIMITATION
        messages = self.__split_list(messages, size=100)

        try:
            for m in messages:
                await self.bot.http.delete_messages(channel_id=channel, message_ids=m, reason=reason)

        except discord.errors.Forbidden:

            if not quiet:
                self.safe_print("[Warning] Cannot delete message \"{message}\", no permission")

        except discord.errors.NotFound:
            if not quiet:
                self.safe_print("[Warning] Cannot delete message \"{message}\", message not found")

        return

    async def __del_msg_later(self, message, after):
        """Custom function to delete messages after a period of time"""

        await asyncio.sleep(after)
        await self.delete_msg(message)
        return

# ======================================== Misc ========================================
    def safe_print(self, content, *, end='\n', flush=True):
        """Custom function to allow printing to console with less issues from asyncio"""

        sys.stdout.buffer.write((content + end).encode('utf-8', 'replace'))
        if flush:
            sys.stdout.flush()


    async def __split_list(self, arr, size=100):
        """Custom function to break a list or string into an array of a certain size"""

        arrs = []

        while len(arr) > size:
            pice = arr[:size]
            arrs.append(pice)
            arr = arr[size:]

        arrs.append(arr)
        return arrs

    async def _has_guild_perms(self, member, perm):
        """
        Input:
            member: member of a guild 
            perm: name of perm as list below.

        Output:
            True:   if member has specified perm
            False:  if member is not member type
                    or member does not have specified perm
                    or specified perm does not exist
        """

        if not isinstance(member, discord.Member):
            return False

        raw_perms = ["create_instant_invite", "kick_members", "ban_members", "administrator", "manage_channels",
                    "manage_server","add_reactions", "view_audit_logs", "", "", "read_messages", "send_messages",
                    "send_tts_messages", "manage_messages", "embed_links", "attach_files", "read_message_history",
                    "mention_everyone", "external_emojis", "", "connect", "speak", "mute_members", "deafen_members",
                    "move_members", "use_voice_activation", "change_nickname", "manage_nicknames", "manage_roles",
                    "manage_webhooks", "manage_emojis"]

        try:
            sel_perm = raw_perms.index(perm)

        except ValueError:
            return False

        for role in member.roles:
            if bool((role.permissions.value >> sel_perm) & 1):
                return True 

        return False