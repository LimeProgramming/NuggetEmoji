class DatabaseCmds(object):

  # ============================== EMOJI TABLE ============================== 
    CREATE_EMOJI_TABLE = '''
        CREATE TABLE IF NOT EXISTS "emoji_list" (
            "e_id"            BIGINT          PRIMARY KEY,
            "name"            VARCHAR(100)    NOT NULL,
            "animated"        BOOLEAN         NOT NULL,
            "image"           DISCORD_IMG,
            "available"       BOOLEAN         DEFAULT TRUE,
            "uploader"        BIGINT,      
            "created_at"      DATETIME       DEFAULT datetime('now', 'utc'),
            "src_guild"       BIGINT,
            "src_image_name"  VARCHAR(100),
            "vaultify"        BOOLEAN         DEFAULT TRUE
        );
        '''


  # ============================== WEBHOOKS TABLE ============================== 

    CREATE_WEBHOOK_TABLE = """ 
        CREATE TABLE IF NOT EXISTS "webhooks" (
            "id"        BIGINT,
            "token"     VARCHAR(100),
            "ch_id"     BIGINT,
            "timestamp" DATETIME        DEFAULT datetime('now', 'utc'),
            PRIMARY KEY("id")
        );
        """

    EXISTS_WEBHOOK_TABLE=       "SELECT EXISTS(SELECT name FROM sqlite_master WHERE type='table' AND name='webhooks');"
    GET_WEBHOOK=                "SELECT id, token FROM webhooks WHERE ch_id = CAST($1 as BIGINT) LIMIT 1" 
    SET_WEBHOOK="""
        INSERT INTO webhooks(
            id, token, ch_id
            )
        VALUES(
            CAST($1 AS BIGINT), CAST($2 AS VARCHAR(100)), CAST($3 AS BIGINT)
            )
        ON CONFLICT(id)
            DO UPDATE
            SET 
                id = 		    CAST($1 AS BIGINT),
                token = 		CAST($2 AS VARCHAR(100)),
                timestamp =		datetime('now', 'utc')

            WHERE 
                webhooks.ch_id = 	    CAST($3 AS BIGINT);
        """