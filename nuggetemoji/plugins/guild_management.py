import sys
import json
import discord
import asyncio
import datetime

from discord.ext import commands
from nuggetemoji.util import dataclasses
from .util import checks
from .util.misc import RANDOM_DISCORD_COLOUR, AVATAR_URL_AS, GUILD_URL_AS
from nuggetemoji.util.allowed_mentions import AllowedMentions


class GuildManagement(commands.Cog):
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


  # -------------------- Listeners -------------------- 

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
      # ---------- If using SQLite database ----------
        if self.bot.config.use_sqlite and len(self.bot.guilds) >= self.bot.config.sqlitelimit:
            owner = guild.owner
            
            try:
                await owner.send("Unfortunately I cannot join your awesome Discord server because of limitations of my database. \n I'll be leaving now. 👋")
            except Exception:
                pass

            bot_owner = await self.bot.application_info().owner

            try:
                await bot_owner.send(f"I failed to join another guild. I could not join {guild.name} because I am at my max limit of guilds while using SQLite. If you want me to be able to join more servers, consider switched to PostgreSQL database which has unlimited guilds.")
            except Exception:
                pass

            await guild.leave()
            return 

      # ---------- Setup variables ----------
        bot_member = guild.get_member(self.bot.user.id)
        bot_ava = await self.bot.user.avatar_url_as(format="png", size=128).read()
        guild_issues = []

        gsguild = dataclasses.Guild(
            name=               guild.name, 
            id=                 guild.id, 
            prefix =            self.bot.config.command_prefix, 
            allowed_roles =     [], 
            allow_mentions =    False, 
            allow_everyone =    False    
            )

        await self.bot.db.add_guild_settings(guild, prefix=self.bot.config.command_prefix)

      # ---------- Sort out the webhooks ----------
        # ===== Iter guilds text channels to sort out the guilds webhooks.
        for channel in guild.text_channels:

            # === If bot cannot manage_webhooks.
            if not channel.permissions_for(bot_member).manage_webhooks:
                guild_issues.append(f"Missing Manage Webhooks permissions in <#{channel.id}.")
                continue 
            
            # === Get the channels existing webhooks
            webhooks = await channel.webhooks()
            
            # --------------------------------------------------
            # === If channel has no webhooks it's safe to assume that we have to make one.
            if len(webhooks) == 0:
                # - Create webhook
                hook = await self.bot._create_webhook(channel, bot_ava)
                # - Write webhook to database
                await self.bot.db.set_webhook(id = hook.id, token = hook.token, ch_id=channel)
                # - Write webhook to guild dataclass
                gsguild.set_webhook2(dataclasses.Webhook(id = hook.id, token = hook.token, ch_id = channel.id))
                # - Move onto the next channel
                continue
            
            # --------------------------------------------------
            # === Try to find a webhook the bot made and pick one.
            try: 
                hook = [webhook for webhook in webhooks if webhook.user == self.bot.user].pop()
            
            except IndexError:
                # - Create webhook if bot didn't make any of the channels webhooks.
                hook = await self.bot._create_webhook(channel, bot_ava)
            
            finally:
                # - Store the webhook in database
                await self.bot.db.set_webhook(hook.id, hook.token, channel) 
                gsguild.set_webhook(channel.id, hook.id, hook.token)

        # ===== Add guild to guild_settings.
        self.bot.guild_settings.add_guild(gsguild)


      # ---------- Deal with guilds emotes ----------
        #only way for this to be true is if guild has multiple emojis with the same name.
        if not len(guild.emojis) == len(set([emji.name for emji in guild.emojis])):
            
            edict = {}
            for emji in guild.emojis:
                if emji.name in edict:
                    edict[emji.id].append(emji)
                else:
                    edict[emji.id] = [emji]

            for problemEmojis in [emji for emji in edict.items() if len(emji) > 1]:
                dupeemji = f"More than one emoji with the name {problemEmojis[0].name} "

                for e in problemEmojis:
                    em = f'<{"a" if e.animated else ""}:{e.name}:{e.id}> '
                    dupeemji += em

                guild_issues.append(dupeemji)

      # ---------- DM Guild Owner ----------
        owner = guild.owner

        msg_content = ""

        msg_content = "Thank you for adding me to your server. "
        
        if self.bot.config.support_invite is not None:
            msg_content += f"If you want help with the bot join the support discord {self.bot.config.support_invite}"

        if guild_issues:
            msg_content += "I have some one or more issues with your guild.\n```\n\t>"
            msg_content += '\n\t>'.join(guild_issues)
            msg_content += "\n```\nIt is recommended to correct these issue(s). Bot will try to compensate for them none the less."
        
        await owner.send(msg_content)

        return 

    async def on_guild_remove(self, guild):
        await self.bot.db.remove_guild(guild)
        pass