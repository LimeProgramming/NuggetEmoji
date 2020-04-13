from dataclasses import dataclass, field

from discord import TextChannel as DiscordTextChannel
from discord import VoiceChannel as DiscordVoiceChannel
from discord import CategoryChannel as DiscordCategoryChannel
from discord import Guild as DiscordGuild
from discord import Webhook as DiscordWebhook



@dataclass
class GuildSettings:
    guilds: dict = field(default_factory=dict)

    def add_guild(self, guild):
        self.guilds[guild.id] = guild
    
    def get_webhook(self, guild, channel):
        if isinstance(guild, DiscordGuild):
            guild = guild.id 
        
        if isinstance(channel, DiscordTextChannel):
            channel = channel.id

        try:
            return self.guilds[guild].get_webhook[channel]
        except KeyError:
            return None
    
    def set_webhook(self, guild, webhook):
        if isinstance(webhook, DiscordWebhook):
            self.guilds[webhook.guild_id].set_webhook2(Webhook(webhook.id, webhook.token, webhook.channel_id))
            return 

        if isinstance(guild, DiscordGuild):
            guild = guild.id 

        self.guilds[guild].set_webhook2(webhook)
        return
        

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

    def __repr__(self):
        return "<Guild_Settings name={}, guild_id={}>".format(
            repr(self.name),
            self.id,
        )
    
    def set_webhook(self, ch_id:int, w_id:int, w_token:int):
        self.webhooks[ch_id] = Webhook(w_id, w_token, ch_id)
        return

    def set_webhook2(self, webhook):
        self.webhooks[webhook.ch_id] = webhook
        return

    def get_webhook(self, ch_id):
        try:
            return self.webhooks[ch_id]
        except KeyError:
            return None
