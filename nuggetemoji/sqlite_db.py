import discord
import aiosqlite
from enum import Enum
from pathlib import Path

DBPATH = Path.cwd() / "data" / "bot.db"

class DBReturns(Enum):
    SUCCESS =           "Success!"
    ROLEDUPLICIT =      "Role is already allowed."
    INVALIDGUILD =      "Guild data is invalid."
    INVALIDCHANNEL =    "Channel data is invalid."
    INVALIDROLE  =      "Role data is invalid."
    ROLENOTGUILD =      "Role is not in this guild/server."
    
    def __str__(self):
        return self.value

class sqlite_db:
    def __init__(self): 
        #I do nothing lOL
        return

    async def connect(self):
        self.conn = await aiosqlite.connect(str(DBPATH))
        self.conn.row_factory = aiosqlite.Row
        self.cursor = await self.conn.cursor()
        return

    async def close(self):
        try:
            await self.conn.close()
        except ValueError:
            pass
        return

  # ============================== WEBHOOKS TABLE ==============================
    # Adds a guild to the guilds table
    async def create_webhook_table(self):
        sql = """ 
        CREATE TABLE IF NOT EXISTS "webhooks" (
            "id"        BIGINT,
            "token"     VARCHAR(100),
            "ch_id"     BIGINT,
            "guild_id"  BIGINT,
            "timestamp" DATETIME        DEFAULT (DATETIME('now', 'utc')),
            PRIMARY KEY("id"),
            UNIQUE("ch_id")
        );"""

        await self.cursor.execute(sql)
        await self.conn.commit()
        return

    async def get_webhook(self, ch_id):
        sql = "SELECT id, token FROM webhooks WHERE ch_id = CAST(? as BIGINT) LIMIT 1" 

        await self.cursor.execute(sql, (ch_id,))
        
        fetched = await self.cursor.fetchone()
        return fetched

    async def set_webhook(self, id, token, ch_id, guild_id=None):

        sql = """ 
        INSERT INTO webhooks(
            id, token, ch_id
            )
        VALUES(
            CAST(:id AS BIGINT), CAST(:token AS VARCHAR(100)), CAST(:ch_id AS BIGINT), CAST(:guild_id AS BIGINT)
            )
        ON CONFLICT(ch_id)
            DO UPDATE
            SET 
                id = 		    CAST(:id AS BIGINT),
                token = 		CAST(:token AS VARCHAR(100)),
                timestamp =		datetime('now', 'utc')

            WHERE 
                webhooks.ch_id = 	    CAST(:ch_id AS BIGINT);
        """

      # ---------- Sort out of the channel arg ----------
        if isinstance(ch_id, discord.TextChannel):
            guild_id = ch_id.guild.id
            ch_id = ch_id.id

        elif type(ch_id) is str:
            ch_id = ch_id.strip()

            if not ch_id.isdigit():
                return DBReturns.INVALIDCHANNEL  

            ch_id =  int(ch_id)
        
        if not type(ch_id) is int:
            return DBReturns.INVALIDCHANNEL  

      # ---------- Sort out of the guild arg ----------
        if isinstance(guild_id, discord.Guild):
            if guild_id is None:
                guild_id = guild_id.id
        
        elif type(guild_id) is int:
            if not isinstance(ch_id, discord.TextChannel):
                guild_id = guild_id

        elif type(guild_id) is str:
            guild_id = guild_id.strip()

            if not guild_id.isdigit():
                return DBReturns.INVALIDGUILD  
            
            if not isinstance(ch_id, discord.TextChannel):
                guild_id = int(guild_id)

        if guild_id is None:
            return DBReturns.INVALIDGUILD  

        await self.cursor.execute(sql, {"id":id, "token":token, "ch_id":ch_id, "guild_id":guild_id})
        await self.conn.commit()
        return

    async def get_guild_webhooks(self, guild_id):

        sql = "SELECT id, token, ch_id FROM webhooks WHERE guild_id = CAST(? AS BIGINT);"

      # ---------- Sort out of the guild arg ----------
        if isinstance(guild_id, discord.Guild):
            if guild_id is None:
                guild_id = guild_id.id

        elif type(guild_id) is str:
            guild_id = guild_id.strip()

            if not guild_id.isdigit():
                return DBReturns.INVALIDGUILD  

            guild_id = int(guild_id)
        
        if not type(guild_id) is int:
            return DBReturns.INVALIDGUILD 

        await self.cursor.execute(sql, (guild_id,))
        fetched = await self.cursor.fetch()
        return fetched


  # ============================== GUILD TABLE ==============================
    # Adds a guild to the guilds table
    async def create_guild_settings_table(self):
        sql = """ 
        CREATE TABLE IF NOT EXISTS "guild_settings" (
            "guild_id"          BIGINT,
            "prefix"            VARCHAR(100)        DEFAULT ('?'),
            "allowed_roles"     TEXT                DEFAULT (''),
            "allow_mentions"    BOOLEAN             DEFAULT (False),
            "allow_everyone"    BOOLEAN             DEFAULT (False),
            PRIMARY KEY("guild_id")
        );"""

        await self.cursor.execute(sql)
        await self.conn.commit()
        return

    async def get_guild_allowed_roles(self, guild_id):
        sql = "SELECT allowed_roles FROM guild_settings WHERE guild_id = CAST(:guild_id as BIGINT) LIMIT 1;" 

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
        await self.cursor.execute(sql, {"guild_id":guild_id})
        fetched = await self.cursor.fetchone()

        return [int(i) for i in fetched['allowed_roles'].split(',') if i.isdigit()]

    async def set_guild_allowed_roles(self, roles, guild_id):
        sql = """ 
        UPDATE guild_settings
        SET 
            allowed_roles =     CAST(:role_ids AS TEXT)
        WHERE 
            guild_id =          CAST(:guild_id AS BIGINT);
        """

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

        role_ids = ','.join(role_ids)

      # ---------- Set new data ----------
        await self.cursor.execute(sql, {"role_ids":role_ids, "guild_id":guild_id})
        await self.conn.commit()
        return

    async def add_guild_allowed_role(self, role, guild_id):

        sql = "SELECT allowed_roles FROM guild_settings WHERE guild_id = CAST(:guild_id as BIGINT) LIMIT 1;" 

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
        await self.cursor.execute(sql, {"guild_id":guild_id})
        fetched = await self.cursor.fetchone()

      # ---------- Set new sql query ----------
        sql = """ 
        UPDATE guild_settings
        SET 
            allowed_roles =     CAST(:role_ids AS TEXT)
        WHERE 
            guild_id =          CAST(:guild_id AS BIGINT);
        """

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

        if not fetched['allowed_roles']:
            role_ids = role 
        else:
            
            if role in [int(i) for i in fetched['allowed_roles'].split(',') if i.isdigit()]:
                return DBReturns.ROLEDUPLICIT

            role_ids = fetched['allowed_roles'] + "," + role

      # ---------- Set new data ----------
        await self.cursor.execute(sql, {"role_ids":role_ids, "guild_id":guild_id})
        await self.conn.commit()
        return DBReturns.SUCCESS

    async def add_guild_settings(self, guild_id, prefix = "?"):
        sql = """ 
        INSERT INTO guild_settings(
            guild_id, prefix
            )
        VALUES(
            CAST(:guild_id AS BIGINT), CAST(:prefix AS VARCHAR(100))
            )
        ON CONFLICT(guild_id)
            DO UPDATE
            SET
                prefix =        '?',
                allowed_roles=  '';
        """

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

        await self.cursor.execute(sql, {"guild_id":guild_id, 'prefix':prefix})
        await self.conn.commit()
        return DBReturns.SUCCESS
        
    async def set_guild_prefix(self, guild_id, prefix = "?"):
        sql = """ 
        UPDATE guild_settings
        SET 
            prefix =            CAST(:prefix AS VARCHAR(100))
        WHERE 
            guild_id =          CAST(:guild_id AS BIGINT);
        """

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

        await self.cursor.execute(sql, {"guild_id":guild_id, 'prefix':prefix})
        await self.conn.commit()
        return DBReturns.SUCCESS

    async def guild_exists(self, guild_id):
        
        sql = "SELECT EXISTS (SELECT guild_id FROM guild_settings WHERE guild_id = CAST(:guild_id AS BIGINT));"

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
        fetched = await self.conn.fetchrow(sql, {"guild_id":guild_id})

        return fetched[0]

    async def get_all_guild_ids(self):
        sql = "SELECT guild_id FROM guild_settings;"

        fetched = await self.conn.fetch(sql)

        return fetched

    async def remove_guild(self, guild_id):
        sql = """
        DELETE FROM public.guild_settings WHERE guild_id = CAST(:guild_id AS BIGINT);
        DELETE FROM public.webhooks WHERE guild_id = CAST(:guild_id AS BIGINT);
        """
        
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

        await self.conn.execute(sql, {"guild_id":guild_id})
        await self.conn.commit()
        return DBReturns.SUCCESS

    async def get_guild_settings(self, guild_id):
        sql = "SELECT * FROM guild_settings WHERE guild_id = CAST(:guild_id AS BIGINT) LIMIT 1;"

      # ---------- Sort out of the guild arg ----------
        if isinstance(guild_id, discord.Guild):
            guild_id = guild_id.id

        elif type(guild_id) is int:
            pass

        elif type(guild_id) is str:
            guild_id = guild_id.strip()

            if not guild_id.isdigit():
                return DBReturns.INVALIDGUILD  

            guild_id =  int(guild_id)
        
        if not type(guild_id) is int:
            return DBReturns.INVALIDGUILD

        await self.cursor.execute(sql, {"guild_id":guild_id})
        fetched = await self.cursor.fetchone()
        fetched['allowed_roles'] = [int(i) for i in fetched['allowed_roles'].split(',') if i.isdigit()]

        tfetched = {
            "guild_id":         fetched['guild_id'],
            "prefix":           fetched['prefix'],
            "allowed_roles":    [int(i) for i in fetched['allowed_roles'].split(',') if i.isdigit()],
            "allow_mentions":   fetched['allow_mentions'],
            "allow_everyone":   fetched['allow_everyone'],
        }
        del fetched 
        return tfetched

    async def get_boot_guild_settings(self, guild_id):
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

      # ---------- Get guild settings from guild_settings table ----------
        f1 = await self.get_guild_settings(guild_id)

      # ---------- Get webhooks from webhooks table ----------
        f2 = await self.get_guild_webhooks(guild_id)

        hooks = []

        for record in f2:
            hooks.append(
                {
                'id':       record['id'], 
                'token':    record['token'],
                'ch_id':    record['ch_id']
                }
            )
        
        f1['webhooks'] = hooks

        return f1
        
  # ============================== COMPOSITE TYPES ==============================
    async def create_webhook_type(self):
        return