import discord
import asyncpg
import logging
from enum import Enum
from pathlib import Path

from . import pg_cmds
from .util import exceptions

dblog = logging.getLogger("pgDB")

class DBReturns(Enum):
    SUCCESS =       "Success!"
    ROLEDUPLICIT =  "Role is already allowed."
    INVALIDGUILD =  "Guild data is invalid."
    INVALIDROLE  =  "Role data is invalid."
    ROLENOTGUILD =  "Role is not in this guild/server."
    
    def __str__(self):
        return self.value

class pg_db:
    def __init__(self, user, pwrd, name, host): 
        self.user = user 
        self.pwrd = pwrd
        self.name = name 
        self.host = host
        #I do nothing lOL
        return

    async def connect(self):

        # ===== LOG INTO DATABASE
        credentials = {"user": self.user, "password": self.pwrd, "database": self.name, "host": self.host}
        try:
            self.conn = await asyncpg.create_pool(**credentials)
        except Exception as e:
            dblog.critical(f"There was an error connecting to the database {e}\nPlease make sure the login information in dblogin.ini is correct.")

            self.exit_signal = exceptions.TerminateSignal

        return

    async def close(self):
        await self.conn.close()


  # ============================== WEBHOOKS TABLE ==============================
    # Adds a guild to the guilds table
    async def create_webhook_table(self):
        await self.conn.execute(pg_cmds.CREATE_WEBHOOK_TABLE)
        return

    async def get_webhook(self, ch_id):
        fetched = await self.conn.fetchrow(pg_cmds.GET_WEBHOOK, ch_id)
        return fetched

    async def set_webhook(self, id, token, ch_id):
        await self.conn.execute(pg_cmds.SET_WEBHOOK, id, token, ch_id)
        return


  # ============================== GUILD TABLE ==============================
    # Adds a guild to the guilds table
    async def create_guild_settings_table(self):
        await self.conn.execute(pg_cmds.CREATE_GUILD_SETTINGS_TABLE)
        return

    async def get_guild_allowed_roles(self, guild_id):

      # ---------- Sort out of the guild arg ----------
        if isinstance(guild_id, discord.Guild):
            guild_id = guild_id.id

        elif type(guild_id) is str:
            guild_id = guild_id.strip()

            if not guild_id.isdigit():
                return DBReturns.INVALIDGUILD

            guild_id =  int(guild_id)
        
        if not type(guild_id) is int:
            return DBReturns.INVALIDGUILD 

      # ---------- Get exsiting data ----------
        fetched = await self.conn.fetchval(pg_cmds.GET_GUILD_ALLOWED_ROLES, guild_id)

        return fetched

    async def set_guild_allowed_roles(self, roles, guild_id):

      # ---------- Sort out of the guild arg ----------
        if isinstance(guild_id, discord.Guild):
            guild_id = guild_id.id

        elif type(guild_id) is str:
            guild_id = guild_id.strip()

            if not guild_id.isdigit():
                return DBReturns.INVALIDGUILD 

            guild_id =  int(guild_id)
        
        if not type(guild_id) is int:
            return DBReturns.INVALIDGUILD 

      # ---------- Sort out of the roles arg ----------
        role_ids = []
        for i in roles:

            if isinstance(i, discord.Role):
                if not i.guild.id == guild_id:
                    continue

                role_ids.append(str(i.id))

            elif type(i) is str:
                if i.isdigit():
                    role_ids.append(i)
            
            elif type(i) is  int:
                role_ids.append(str(i))

        if len(role_ids) == 0:
            return DBReturns.INVALIDROLE 

      # ---------- Set new data ----------
        await self.conn.execute(pg_cmds.SET_GUILD_ALLOWED_ROLES, role_ids, guild_id)
        return DBReturns.SUCCESS

    async def add_guild_allowed_role(self, role, guild_id):

      # ---------- Sort out of the guild arg ----------
        if isinstance(guild_id, discord.Guild):
            guild_id = guild_id.id

        elif type(guild_id) is str:
            guild_id = guild_id.strip()

            if not guild_id.isdigit():
                return DBReturns.INVALIDGUILD 

            guild_id =  int(guild_id)
        
        if not type(guild_id) is int:
            return DBReturns.INVALIDGUILD 

      # ---------- Sort out of the role arg ----------
        if isinstance(role, discord.Role):
            if not role.guild.id == guild_id:
                return DBReturns.ROLENOTGUILD
            role = str(role.id)

        elif type(role) is str:
            role = role.strip()

            if not role.isdigit():
                return DBReturns.INVALIDROLE
                
        elif type(role) is int:
            role = str(role)

      # ---------- Get exsiting data ----------
        fetched = await self.conn.fetchval(pg_cmds.GET_GUILD_ALLOWED_ROLES, guild_id)

      # ---------- If role is already allowed ----------
        if role in fetched:
            return DBReturns.ROLEDUPLICIT

      # ---------- Set new data ----------
        await self.conn.execute(pg_cmds.APPEND_GUILD_ALLOWED_ROLE, role, guild_id)
        return DBReturns.SUCCESS

    async def add_guild_settings(self, guild_id, prefix):

      # ---------- Sort out of the guild arg ----------
        if isinstance(guild_id, discord.Guild):
            guild_id = guild_id.id

        elif type(guild_id) is str:
            guild_id = guild_id.strip()

            if not guild_id.isdigit():
                return DBReturns.INVALIDGUILD  

            guild_id =  int(guild_id)
        
        if not type(guild_id) is int:
            return DBReturns.INVALIDGUILD  

      # ---------- Sort out the prefix arg ----------
        prefix = prefix or "?"

        await self.conn.commit(pg_cmds.ADD_GUILD_SETTINGS, guild_id, prefix)
        return DBReturns.SUCCESS

    async def set_guild_prefix(self, guild_id, prefix):

      # ---------- Sort out of the guild arg ----------
        if isinstance(guild_id, discord.Guild):
            guild_id = guild_id.id

        elif type(guild_id) is str:
            guild_id = guild_id.strip()

            if not guild_id.isdigit():
                return DBReturns.INVALIDGUILD  

            guild_id =  int(guild_id)
        
        if not type(guild_id) is int:
            return DBReturns.INVALIDGUILD 

      # ---------- Sort out the prefix arg ----------
        prefix = prefix or "?"

        await self.conn.execute(pg_cmds.SET_GUILD_PREFIX, guild_id, prefix)

        return DBReturns.SUCCESS