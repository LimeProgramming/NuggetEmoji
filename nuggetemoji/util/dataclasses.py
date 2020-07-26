from dataclasses import dataclass, field

from discord import TextChannel as DiscordTextChannel
from discord import VoiceChannel as DiscordVoiceChannel
from discord import CategoryChannel as DiscordCategoryChannel
from discord import Guild as DiscordGuild
from discord import Webhook as DiscordWebhook



@dataclass
class GuildSettings:
    guilds: dict = field(default_factory=dict)

  # ---------- Guild Functions ----------
    def add_guild(self, guild):
        self.guilds[guild.id] = guild
    
    def get_guild(self, guild):
        guild = guild.id if isinstance(guild, DiscordGuild) else guild
        
        return self.guilds.get(guild, None)

    def del_guild(self, guild):
        guild = guild.id if isinstance(guild, DiscordGuild) else guild

        self.guilds.pop(guild, None)

        return 

  # ---------- Webhook Functions ----------
    def get_webhook(self, guild, channel):
        guild = guild.id if isinstance(guild, DiscordGuild) else guild
        channel = channel.id if isinstance(channel, DiscordTextChannel) else channel

        try:
            return self.guilds[guild].get_webhook(channel)
        except KeyError:
            return None
    
    def set_webhook(self, guild, webhook):
        if isinstance(webhook, DiscordWebhook):
            self.guilds[webhook.guild_id].set_webhook2(Webhook(webhook.id, webhook.token, webhook.channel_id))
            return 

        guild = guild.id if isinstance(guild, DiscordGuild) else guild

        self.guilds[guild].set_webhook2(webhook)
        return
    
    def del_webhook(self, guild, webhook):
        guild = guild.id if isinstance(guild, DiscordGuild) else guild

        try:
            self.guilds[guild].del_webhook(webhook)
        except KeyError:
            return None

@dataclass
class Webhook:
    id: int
    token: str
    ch_id: int


@dataclass
class Guild:
    name: str
    id: int
    prefix: str = '?'
    allowed_roles: list = field(default_factory=list)
    allow_mentions: bool = False
    allow_everyone: bool = False
    webhooks: dict = field(default_factory=dict)

    #def __repr__(self):
    #    return "<Guild_Settings name={}, guild_id={}>, prefix={}, allowed_roles={}".format(
    #        repr(self.name),
    #        self.id,
    #    )
    
    def set_webhook(self, ch_id:int, w_id:int, w_token:int):
        self.webhooks[ch_id] = Webhook(w_id, w_token, ch_id)
        return

    def set_webhook2(self, webhook):
        self.webhooks[webhook.ch_id] = webhook
        return

    def get_webhook(self, ch_id):
        return self.webhooks.get(ch_id, None)

    def del_webhook(self, webhook):
        try:
            del self.webhooks[webhook.ch_id]
        except KeyError:
            pass 
        finally:
            return