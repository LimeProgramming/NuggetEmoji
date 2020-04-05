#import re
import sys
#'import json
import random
import asyncio
import aiohttp
import discord
import logging
import pathlib
import datetime
import traceback
from typing import Union
from discord.ext import commands
from collections.abc import Iterable

from .config import Config
from .util import exceptions
from .util.misc import Response
from .util import gen_embed as GenEmbed
from .util import fake_objects as FakeOBJS
from .util.allowed_mentions import AllowedMentions




import dblogin
import asyncpg
from .db_cmds import DatabaseCmds as pgCmds

import aiosqlite
from .test_db import sqlite_db


logging.basicConfig(level=logging.INFO)
dblog = logging.getLogger("pgDB")
#log = logging.getLogger("bot")
#log = logging.getLogger(__name__)

description = """
NuggetBot4.0
A bot made for FurSail
Made by Calamity Lime#8500
"""

plugins = (
    ('nuggetemoji.plugins.test',       'Test'),
    ('nuggetemoji.plugins.owner',      'Owner'),
    ('nuggetemoji.plugins.admin',      'Admin'),
)

class NuggetEmoji(commands.Bot):

    RafEntryActive = False
    RafDatetime = {}
    reactionmsgs = ""

# ======================================== Bot Object Setup ========================================
    def _cleanup(self):
        try:
            self.loop.run_until_complete(self.logout())
        except: pass

        pending = asyncio.Task.all_tasks()
        gathered = asyncio.gather(*pending)

        try:
            gathered.cancel()
            self.loop.run_until_complete(gathered)
            gathered.exception()
        except: pass

    # noinspection PyMethodOverriding
    def run(self):
        try:
            self.loop.run_until_complete(self.start(*self.config.auth))

        except discord.errors.LoginFailure:
            # Add if token, else
            raise exceptions.HelpfulError(
                "Bot cannot login, bad credentials.",
                "Fix your token in the options file.  "
                "Remember that each field should be on their own line."
            )

        finally:
            try:
                self._cleanup()
            except Exception:
                pass
                #log.error("Error in cleanup", exc_info=True)

            self.loop.close()

            if self.exit_signal:
                raise self.exit_signal


# ======================================== Bot init Setup ========================================
    def __init__(self):
        NuggetEmoji.bot = self
        self.config = Config()
        self.init_ok = True
        self.exit_signal = None
        self.AllowedMentions = AllowedMentions(everyone=False)

      # ---------- Store startup timestamp ----------
        self.start_timestamp = datetime.datetime.utcnow()

      # ---------- Store a list of all the legacy bot commands ----------
        self.bot_oneline_commands = ["restart", "shutdown", 'reboot']

        super().__init__(command_prefix='?',            description=description,
                         pm_help=None,                  help_attrs=dict(hidden=True), 
                         fetch_offline_members=False,   )#allowed_mentions=discord.AllowedMentions(everyone=False))

        self.aiosession = aiohttp.ClientSession(loop=self.loop)

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

        return 


# ======================================== Bot on Ready Funcs ========================================



# ======================================== Bot Events ========================================
    async def on_ready(self):
        print('\rConnected!  NuggetEmoji va0.3\n')

        self.safe_print("--------------------------------------------------------------------------------")
        self.safe_print("Bot:   {0.name}#{0.discriminator} \t\t| ID: {0.id}".format(self.user))

        owner = await self._get_owner()

        self.safe_print("Owner: {0.name}#{0.discriminator} \t| ID: {0.id}".format(owner))

        self.safe_print(r"--------------------------------------------------------------------------------")
        self.safe_print(r" _______                              __ ___________                  __.__     ")
        self.safe_print(r" \      \  __ __  ____   ____   _____/  |\_   _____/ _____   ____    |__|__|    ")
        self.safe_print(r" /   |   \|  |  \/ ___\ / ___\_/ __ \   __\    __)_ /     \ /  _ \   |  |  |    ")
        self.safe_print(r"/    |    \  |  / /_/  > /_/  >  ___/|  | |        \  Y Y  (  <_> )  |  |  |    ")
        self.safe_print(r"\____|__  /____/\___  /\___  / \___  >__|/_______  /__|_|  /\____/\__|  |__|    ")
        self.safe_print(r"        \/     /_____//_____/      \/            \/      \/      \______|       ")
        self.safe_print(r"--------------------------------------------------------------------------------")
        self.safe_print("\n")

        #await self.pgdb_on_ready()

        self.test_db = sqlite_db()
        await self.test_db.connect()

        await self.test_db.create_webhook_table()
        await self.test_db.create_guild_settings_table()

        # ----- If bots first run.
        if not pathlib.Path("data/Do Not Delete").exists():
            await self.first_run(owner)


    async def on_resume(self):
        await self.test_db.connect()

        # ===== If the bot is still setting up
        await self.wait_until_ready()

        self.safe_print("Bot resumed")

    async def on_disconnect(self):
        await self.test_db.close()
        return

    async def on_error(self, event, *args, **kwargs):
        ex_type, ex, stack = sys.exc_info()

        if ex_type == exceptions.HelpfulError:
            print("Exception in", event)
            print(ex.message)
            
            await asyncio.sleep(2)
            #await self.db.close()
            await self.logout()
            await self.close()

        elif ex_type == discord.ext.commands.errors.CommandInvokeError:
            if issubclass(type(ex.original), exceptions.Signal):

                if type(ex.original) == exceptions.RestartSignal:
                    self.exit_signal = exceptions.RestartSignal()

                elif type(ex.original) == exceptions.TerminateSignal:
                    self.exit_signal = exceptions.TerminateSignal()

                await self.test_db.close()
                #await self.db.close()

                await self.logout()
                await self.close()

        elif issubclass(ex_type, exceptions.Signal):
            self.exit_signal = ex_type
            await self.test_db.close()
            #await self.db.close()
            await self.logout()
            await self.close()

        elif ex_type == exceptions.PostAsWebhook:

            channel = self.get_channel(614956834771566594)
            Webhook = discord.utils.get(await channel.webhooks(), name='NugBotErrors')

            await Webhook.send(
                content=        ex.message,
                username=       "NuggetBotErrors",
                avatar_url=     self.user.avatar_url,
                tts=            False,
                files=          None,
                embeds=         None
            )

        else:
            print('Ignoring exception in {}'.format(event), file=sys.stderr)
            traceback.print_exc()
            #pass
           # print(stack)

    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.PrivateMessageOnly):

            await ctx.channel.send(f'`Command "{ctx.message.content.split(" ")[0]}" only works in DM\'s.`', delete_after=15)

            if self.config.delete_invoking:
                await ctx.message.delete()

        else:
            print('Ignoring exception in {}'.format(ctx.invoked_with), file=sys.stderr)
            print(error)

        return

    async def first_run(self, owner):
        await owner.send("Thank you for bringing me to life.")

        with open("data/Do Not Delete", 'w') as f:
            f.write("Unless you want the bot to reinitialize")


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
    async def send_msg2(self, 
        dest:Union[discord.TextChannel, discord.Message, discord.ext.commands.Context, int], *, 
        content=None, 
        embed=None, 
        tts=False, 
        delete_after=0,
        also_delete:discord.Message =None, 
        allowed_mentions=None,
        quiet=True):
        
      # ---------- Sort out dest arg ---------- 
        channel = await self._get_channel(dest)

      # ---------- Sort out Allowed Mentions ---------- 
        if allowed_mentions is not None:
            if self.AllowedMentions is not None:
                allowed_mentions = self.AllowedMentions.merge(allowed_mentions).to_dict()
            else:
                allowed_mentions = allowed_mentions.to_dict()
        else:
            allowed_mentions = self.AllowedMentions.to_dict()

      # ---------- Sort out dest arg ---------- 
        msg = None

        try:
            data = await self.send_msg_rqt(channel.id, content, tts=tts, embed=embed, allowed_mentions=allowed_mentions)
            msg = self._connection.create_message(channel=channel, data=data)

            if also_delete and isinstance(also_delete, discord.Message):
                asyncio.ensure_future(self.__del_msg_later(also_delete, delete_after))

            if delete_after:
                asyncio.ensure_future(self.__del_msg_later(msg, delete_after))

        except discord.Forbidden:
            if not quiet:
                self.safe_print("[Warning] Cannot send message to {dest.name}, no permission")

        except discord.NotFound:
            if not quiet:
                self.safe_print("[Warning] Cannot send message to {dest.name}, invalid channel?")

        return msg


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

  # -------------------- Custom Webhook Handling --------------------
    @asyncio.coroutine
    async def execute_webhook(self, webhook:discord.Webhook, content:str, username:str = None, avatar_url:Union[discord.Asset, str] = None, embed:discord.Embed = None, embeds = None, tts:bool = False):
        '''
        Custom discord.Webhook executer. 
        Using this webhook executer forces the discord.py libaray to POST a webhook using the http.request function rather than the request function built into WebhookAdapter.
        The big difference between the two functions is that http.request preforms the POST with an "Authorization" header which allows for the use of emojis and other bot level privilages.
        
        Parameters
        ------------
        webhook :class:`discord.Webhook`
            The webhook you want to POST to.
        content :class:`str`
            Content of the POST message
        username Optional[:class:`str`]
            Username to post the webhook under. Overwrites the default name of the webhook.
        avatar_url Optional[:class:`discord.Asset`]
            Avatar for the webhook poster. Overwrites the default avatar of the webhook.
        embed Optional[:class:`discord.Embed`]
            discord Embed opject to post.
        embeds List[:class:`discord.Embed`]
            List of discord Embed object to post, maximum of 10 allowable.
        tts :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        '''

        if embeds is not None and embed is not None:
            raise discord.errors.InvalidArgument('Cannot mix embed and embeds keyword arguments.')

        payload = {
            'tts':tts
        }

        if content is not None:
            payload['content'] = str(content).replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")

        if username:
            payload['username'] = username

        if avatar_url:
            payload['avatar_url'] = str(avatar_url)

        if embeds is not None:
            if len(embeds) > 10:
                raise discord.errors.InvalidArgument('embeds has a maximum of 10 elements.')
            payload['embeds'] = [e.to_dict() for e in embeds]

        if embed is not None:
            payload['embeds'] = [embed.to_dict()]


        await self.bot.http.request(route=discord.http.Route('POST', f'/webhooks/{webhook.id}/{webhook.token}'), json=payload)

        return

    @asyncio.coroutine
    async def execute_webhook3(self, channel:discord.TextChannel, content:str, username:str = None, avatar_url:Union[discord.Asset, str] = None, embed:discord.Embed = None, embeds = None, files = None, tts:bool = False):
        '''
        Custom discord.Webhook executer. 
        Using this webhook executer forces the discord.py libaray to POST a webhook using the http.request function rather than the request function built into WebhookAdapter.
        The big difference between the two functions is that http.request preforms the POST with an "Authorization" header which allows for the use of emojis and other bot level privilages.
        
        Parameters
        ------------
        webhook :class:`discord.Webhook`
            The webhook you want to POST to.
        content :class:`str`
            Content of the POST message
        username Optional[:class:`str`]
            Username to post the webhook under. Overwrites the default name of the webhook.
        avatar_url Optional[:class:`discord.Asset`]
            Avatar for the webhook poster. Overwrites the default avatar of the webhook.
        embed Optional[:class:`discord.Embed`]
            discord Embed opject to post.
        embeds List[:class:`discord.Embed`]
            List of discord Embed object to post, maximum of 10 allowable.
        tts :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        '''
        # ---------- SORTOUT THE PAYLOAD ----------
        if embeds is not None and embed is not None:
            raise discord.errors.InvalidArgument('Cannot mix embed and embeds keyword arguments.')

        payload = {
            'tts':tts,
            "allowed_mentions": {
                "parse": ["everyone"],
                "users": [],
                "roles": [654438136629166140]
            }
        }

        if content is not None:
            payload['content'] = str(content)#.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
        
        if username:
            payload['username'] = username

        if avatar_url:
            payload['avatar_url'] = str(avatar_url)

        if embeds is not None:
            if len(embeds) > 10:
                raise discord.errors.InvalidArgument('embeds has a maximum of 10 elements.')
            payload['embeds'] = [e.to_dict() for e in embeds]

        if embed is not None:
            payload['embeds'] = [embed.to_dict()]

        # ---------- GET WEBHOOK FROM DB ----------
    

        r = await self.test_db.get_webhook(channel.id)

        if not r:
            ava = await self.user.avatar_url_as(format="png", size=128).read()
            newWebhook = await channel.create_webhook(name='SQLite', avatar=ava, reason='Used by NuggetBot to post webhooks.')

            webhook_id = newWebhook.id
            webhook_token = newWebhook.token

            await self.test_db.set_webhook(webhook_id, webhook_token, channel.id)

        else: webhook_id, webhook_token = r

        # ---------- SORT OUT FILES ----------
        cleanup = None
        cleanup_files = [] 

        form = aiohttp.FormData()
        form.add_field('payload_json', discord.utils.to_json(payload))

        if files is not None:
            for i, file in enumerate(files, start=1):
                if isinstance(file, discord.message.Attachment):
                    filename = file.filename
                    fp = await file.read()

                elif isinstance(file, discord.File):
                    cleanup_files.append(file)
                    filename = file.filename, 
                    fp = file.fp
                
                elif isinstance(file, Iterable):
                    filename = file[0]
                    fp = file[1]        

                form.add_field('file%i' % i, fp, filename=filename, content_type='application/octet-stream')
        
            def _anon():
                for f in cleanup_files:
                    f.close()

            cleanup = _anon

        try:
            await self.bot.http.request(route=discord.http.Route('POST', f'/webhooks/{webhook_id}/{webhook_token}'), data=form)
        
        except discord.errors.HTTPException as e:
            print(e)
            print("http")
            pass

        finally:
            if cleanup:
                cleanup()

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

    async def _get_owner(self):
        return (await self.application_info()).owner

    async def _get_channel(self, dest):
        """
        This just takes common ABC messageables and returns the channel.
        Also suppors channel ids in the form of int's and strings.
        """
        channel = None 

        if isinstance(dest, discord.Message):
            channel = dest.channel 
        
        elif isinstance(dest, discord.TextChannel):
            channel = dest
        
        elif isinstance(dest, discord.ext.commands.Context):
            channel = dest.channel
        
        elif type(dest) is int:
            channel = self.get_channel(dest)
            if channel is None:
                try:
                    channel = self.fetch_channel(dest)
                except (discord.InvalidData, discord.HTTPException, discord.NotFound, discord.Forbidden):
                    channel = None 

        elif type(dest) is str and dest.isdigit():
            dest = int(dest)
            channel = self.get_channel(dest)
            if channel is None:
                try:
                    channel = self.fetch_channel(dest)
                except (discord.InvalidData, discord.HTTPException, discord.NotFound, discord.Forbidden):
                    channel = None 

        return channel

# ======================================== HTTP Replacements ========================================
# Lets be honest, Rapptz is too busy being a weeabo to make these any good.

    async def send_msg_rqt(self, channel_id, content, *, tts=False, embed=None, nonce=None, allowed_mentions=None):

        r = discord.http.Route('POST', '/channels/{channel_id}/messages', channel_id=channel_id)

        payload = {}

        if content:
            payload['content'] = content

        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions

        if tts:
            payload['tts'] = True

        if embed:
            payload['embed'] = embed

        if nonce:
            payload['nonce'] = nonce

        return await self.bot.http.request(r, json=payload)

    def send_files(self, channel_id, *, files, content=None, tts=False, embed=None, nonce=None):
        r = discord.http.Route('POST', '/channels/{channel_id}/messages', channel_id=channel_id)

        form = aiohttp.FormData()

        payload = {'tts': tts}
        if content:
            payload['content'] = content
        if embed:
            payload['embed'] = embed
        if nonce:
            payload['nonce'] = nonce

        form.add_field('payload_json', discord.utils.to_json(payload))
        if len(files) == 1:
            file = files[0]
            form.add_field('file', file.fp, filename=file.filename, content_type='application/octet-stream')
        else:
            for index, file in enumerate(files):
                form.add_field('file%s' % index, file.fp, filename=file.filename, content_type='application/octet-stream')

        return self.bot.http.request(r, data=form, files=files)