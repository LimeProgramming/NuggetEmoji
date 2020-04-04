import discord
import datetime
from . import checkexc 
from functools import wraps
from discord.ext import commands
from collections.abc import Iterable
from .misc import GUILD_URL_AS, AVATAR_URL_AS, RANDOM_DISCORD_COLOR


##Permissions decor | guild owner only
def GUILD_ONLY(*args):
    async def pred(ctx):
        if not ctx:
            return False   

        if ctx.guild:
            return True

        await ctx.channel.send(embed=await __gen_guildonly_embed(ctx))
        return False

    return commands.check(pred)

# -------------------- STAFF DECORS --------------------
##Permissions decor | guild owner only
def GUILD_OWNER(*args):
    async def pred(ctx):
        if not ctx or not ctx.guild:
            return False   

        if ctx.guild.owner == ctx.author:
            return True

        else:
            await ctx.channel.send(embed=await __gen_guildowner_embed(ctx), delete_after=30)
            return False

    return commands.check(pred)

def BOT_OWNER(*args):
    async def pred(ctx):
        if not ctx or not ctx.guild:
            return False   

        if await ctx.bot.is_owner(ctx.author):
            return True

        else:
            await ctx.channel.send(embed=await __gen_botowner_embed(ctx), delete_after=30)
            return False

    return commands.check(pred)

def HAS_PERMISSIONS(**perms):

    # ----- doing this instead of discord.Permissions.VALID_FLAGS to stop IDE from complaining.
    invalid = set(perms) - set([i[0] for i in discord.Permissions()])

    if invalid:
        raise TypeError('Invalid permission(s): %s' % (', '.join(invalid)))

    async def pred(ctx):
        permissions = ctx.channel.permissions_for(ctx.author)
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

        if not missing:
            return True

        await ctx.send(embed=await __gen_missingperms_embed(ctx, missing), delete_after=30)
        return False

    return commands.check(pred)



# -------------------- EMBED GENERATORS --------------------

async def __gen_guildowner_embed(ctx):
    embed = discord.Embed(  
        title=      ':warning: You do not own this guild',
        description="",
        type=       'rich',
        timestamp=  datetime.datetime.utcnow(),
        color=      RANDOM_DISCORD_COLOR()
        )

    embed.set_footer(       
        icon_url=   GUILD_URL_AS(ctx.guild),
        text=       ctx.guild.name
        )
        
    embed.add_field(    
        name=       "Error:",
        value=      f"```\nYou are not the owner of this guild, contact {ctx.guild.owner.name}#{ctx.guild.owner.discriminator} if a command needs to be preformed.\n```",
        inline=     False
        )
    
    return embed

async def __gen_botowner_embed(ctx):
    embed = discord.Embed(  
        title=      ':warning: You do not own me.',
        description="",
        type=       'rich',
        timestamp=  datetime.datetime.utcnow(),
        color=      RANDOM_DISCORD_COLOR()
        )

    embed.set_footer(       
        icon_url=   GUILD_URL_AS(ctx.guild),
        text=       ctx.guild.name
        )
        
    embed.add_field(    
        name=       "Error:",
        value=      f"```\nOnly the bot owner can run {ctx.invoked_with}\n```",
        inline=     False
        )
    
    return embed

async def __gen_missingperms_embed(ctx, missing_perms):
    embed = discord.Embed(  
        title=      ':warning: Missing Permissions',
        description="",
        type=       'rich',
        timestamp=  datetime.datetime.utcnow(),
        color=      RANDOM_DISCORD_COLOR()
        )

    embed.set_footer(       
        icon_url=   GUILD_URL_AS(ctx.guild),
        text=       ctx.guild.name
        )
        
    embed.add_field(    
        name=       "Error:",
        value=      "```\nYou are missing the following permission(s) to run command \"{}\"\n{}\n```".format(
                        ctx.invoked_with, '\n'.join(['>'+i.capitalize() for i in missing_perms])),
        inline=     False
        )

    return embed

async def __gen_guildonly_embed(ctx):
    embed = discord.Embed(  
        title=      ':x: Guild Only Command',
        description="",
        type=       'rich',
        timestamp=  datetime.datetime.utcnow(),
        color=      RANDOM_DISCORD_COLOR()
        )

    embed.add_field(    
        name=       "Error:",
        value=      f"```\nThe command you're trying to run {ctx.invoked_with} only works in guilds/servers.\n```",
        inline=     False
        )

    return embed