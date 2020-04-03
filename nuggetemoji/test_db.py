
import aiosqlite
from pathlib import Path

DBPATH = Path.cwd() / "data" / "bot.db"


class sqlite_db:
    def __init__(self): 
        #I do nothing lOL
        return

    async def bot_ready(self):
        self.conn = await aiosqlite.connect(str(DBPATH))
        self.conn.row_factory = aiosqlite.Row
        self.cursor = await self.conn.cursor()
        return

    async def bot_close(self):
        try:
            await self.conn.close()
        except ValueError:
            pass
        return

    # Adds a guild to the guilds table
    async def create_webhook_table(self):
        sql = """ 
        CREATE TABLE IF NOT EXISTS "webhooks" (
            "id"        BIGINT,
            "token"     VARCHAR(100),
            "ch_id"     BIGINT,
            "timestamp" DATETIME        DEFAULT (DATETIME('now', 'utc')),
            PRIMARY KEY("id")
        );"""

        await self.cursor.execute(sql)
        await self.conn.commit()
        return

    #@staticmethod
    async def get_webhook(self, ch_id):
        sql = "SELECT id, token FROM webhooks WHERE ch_id = CAST(? as BIGINT) LIMIT 1" 

        await self.cursor.execute(sql, (ch_id,))
        
        fetched = await self.cursor.fetchone()
        return fetched

    #@staticmethod
    async def set_webhook(self, id, token, ch_id):

        sql = """ 
        INSERT INTO webhooks(
            id, token, ch_id
            )
        VALUES(
            CAST(:id AS BIGINT), CAST(:token AS VARCHAR(100)), CAST(:ch_id AS BIGINT)
            )
        ON CONFLICT(id)
            DO UPDATE
            SET 
                id = 		    CAST(:id AS BIGINT),
                token = 		CAST(:token AS VARCHAR(100)),
                timestamp =		datetime('now', 'utc')

            WHERE 
                webhooks.ch_id = 	    CAST(:ch_id AS BIGINT);
        """

        await self.cursor.execute(sql, {"id":id, "token":token, "ch_id":ch_id})
        await self.conn.commit()
        return