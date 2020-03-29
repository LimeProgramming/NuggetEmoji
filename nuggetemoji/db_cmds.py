class DatabaseCmds(object):
  # ============================== WEBHOOKS TABLE ============================== 
    CREATE_WEBHOOK_TABLE = """ 
        CREATE TABLE IF NOT EXISTS webhooks (
            id          BIGINT          PRIMARY KEY,
            token       VARCHAR(100),
            ch_id       BIGINT,
            timestamp   TIMESTAMP       DEFAULT TIMEZONE('utc'::text, NOW())
        );

        COMMENT ON TABLE webhooks IS                'Holds a list of webhook id''s, tokens and which channel they are assoiated with. Storing this data would save bandwidth.';
        COMMENT ON COLUMN webhooks.id IS            'ID of the webhook.';
        COMMENT ON COLUMN webhooks.token IS         'Webhook token.';
        COMMENT ON COLUMN webhooks.ch_id IS         'Channel id the webhook is pointing to.';
        """

    EXISTS_WEBHOOK_TABLE=       "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE upper(table_name) = 'WEBHOOKS');"
    GET_WEBHOOK=                "SELECT id, token FROM public.webhooks WHERE ch_id = CAST($1 as BIGINT) LIMIT 1" 
    SET_WEBHOOK="""
        INSERT INTO public.webhooks(
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
                timestamp =		TIMEZONE('utc'::text, NOW())

            WHERE 
                webhooks.ch_id = 	    CAST($3 AS BIGINT);
        """