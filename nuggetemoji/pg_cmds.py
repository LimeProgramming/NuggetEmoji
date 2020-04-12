# ============================== WEBHOOKS TABLE ============================== 
CREATE_WEBHOOK_TABLE = """ 
    CREATE TABLE IF NOT EXISTS webhooks (
        id          BIGINT          PRIMARY KEY,
        token       VARCHAR(100),
        guild_id    BIGINT,
        ch_id       BIGINT,
        timestamp   TIMESTAMP       DEFAULT TIMEZONE('utc'::text, NOW())
    );

    COMMENT ON TABLE webhooks IS                'Holds a list of webhook id''s, tokens and which channel they are assoiated with. Storing this data would save bandwidth.';
    COMMENT ON COLUMN webhooks.id IS            'ID of the webhook.';
    COMMENT ON COLUMN webhooks.token IS         'Webhook token.';
    COMMENT ON COLUMN webhooks.ch_id IS         'Channel id the webhook is pointing to.';
    COMMENT ON COLUMN webhooks.guild_id IS      'Guild id the channel is in.';
    """

GET_WEBHOOK=                "SELECT id, token FROM public.webhooks WHERE ch_id = CAST($1 as BIGINT) LIMIT 1" 
SET_WEBHOOK="""
    INSERT INTO public.webhooks(
        id, token, guild_id, ch_id
        )
    VALUES(
        CAST($1 AS BIGINT), CAST($2 AS VARCHAR(100)), CAST($3 AS BIGINT), CAST($4 AS BIGINT)
        )
    ON CONFLICT(id)
        DO UPDATE
        SET 
            id = 		    CAST($1 AS BIGINT),
            token = 		CAST($2 AS VARCHAR(100)),
            timestamp =		TIMEZONE('utc'::text, NOW())

        WHERE 
            webhooks.ch_id = 	    CAST($3 AS BIGINT);
    """


# ============================== GUILD SETTINGS TABLE ==============================
CREATE_GUILD_SETTINGS_TABLE = """
    CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id            BIGINT              PRIMARY KEY,
    prefix              VARCHAR(100)        DEFAULT '?',
    allowed_roles       BIGINT[]            DEFAULT ARRAY[]::BIGINT[],
    allow_mentions      BOOLEAN             DEFAULT FALSE,
    allow_everyone      BOOLEAN             DEFAULT FALSE
    );
    
    COMMENT ON TABLE guild_settings IS                  'This table holds the settings for all the guilds the bot is on.';
    COMMENT ON COLUMN guild_settings.guild_id IS        'ID of the guild.';
    COMMENT ON COLUMN guild_settings.prefix IS          'Command Prefix for the guild.';
    COMMENT ON COLUMN guild_settings.allowed_roles IS   'Array of roles which are allowed to use this bot, if array is empty the bot assumes that every role is allowed to use the bot.';
    """

SET_GUILD_ALLOWED_ROLES = """
    UPDATE public.guild_settings
    SET 
        allowed_roles =     CAST($1 AS BIGINT[])
    WHERE 
        guild_id =          CAST($2 AS BIGINT);
    """

APPEND_GUILD_ALLOWED_ROLE = """
    UPDATE public.guild_settings
    SET 
        allowed_roles =     ARRAY_APPEND((SELECT allowed_roles FROM public.guild_settings WHERE guild_id = $2), CAST($1 AS BIGINT)) 
    WHERE 
        guild_id =          CAST($2 AS BIGINT);
    """

GET_GUILD_ALLOWED_ROLES = "SELECT allowed_roles FROM public.guild_settings WHERE guild_id = $1"

ADD_GUILD_SETTINGS = """
    INSERT INTO public.guild_settings(
        guild_id, prefix
        )
    VALUES(
        CAST($1 AS BIGINT), CAST($2 AS VARCHAR(100))
        )
    ON CONFLICT (guild_id)
        DO UPDATE
        SET 
            prefix =        '?',
            allowed_roles = ARRAY[]::BIGINT[];
    """

SET_GUILD_PREFIX = """ 
    UPDATE public.guild_settings
    SET 
        prefix =            CAST($2 AS VARCHAR(100))
    WHERE 
        guild_id =          CAST($1 AS BIGINT);
    """

EXISTS_GUILD_DATABASE = "SELECT EXISTS (SELECT guild_id FROM public.guild_settings WHERE guild_id = CAST($1 AS BIGINT));"

GET_ALL_GUILD_IDS = "SELECT guild_id FROM public.guild_settings;"
REMOVE_GUILD_INFO = "DELETE FROM public.guild_settings WHERE guild_id = CAST($1 AS BIGINT);"


# ============================== EMOJIS TABLE ==============================
CREATE_EMOJIS_TABLE = """
    CREATE TABLE IF NOT EXISTS emojis (
    emoji_id        BIGINT              PRIMARY KEY,
    guild_id        BIGINT              DEFAULT '?',
    name            VARCHAR(50),
    animated        BOOLEAN,
    url             VARCHAR(100)
    );
    """