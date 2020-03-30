class DatabaseCmds(object):

  # ============================== EMOJI TABLE ============================== 
    CREATE_EMOJI_TABLE = """
        CREATE TABLE IF NOT EXISTS emoji_list (
            e_id            BIGINT          PRIMARY KEY,
            name            VARCHAR(100)    NOT NULL,
            animated        BOOLEAN         NOT NULL,
            image           DISCORD_IMG,
            available       BOOLEAN         DEFAULT TRUE,
            uploader        BIGINT,      
            created_at      TIMESTAMP       DEFAULT TIMEZONE('utc'::text, NOW()),
            src_guild       BIGINT,
            src_image_name  VARCHAR(100),
            vaultify        BOOLEAN         DEFAULT TRUE
        );

        COMMENT ON TABLE emoji_list IS                  'Holds information of all the emojis the bot can access. Storing this data would save bandwidth.';
        COMMENT ON COLUMN emoji_list.e_id IS            'ID of the emote.';
        COMMENT ON COLUMN emoji_list.name IS            'Emote name, the one it is called with.';
        COMMENT ON COLUMN emoji_list.image IS           'Stored bytes of the emoji image. Stored here for the sake of the Vault.';
        COMMENT ON COLUMN emoji_list.src_guild IS       'Guild the emoji is actually presant in.';
        COMMENT ON COLUMN emoji_list.src_image_name IS  'Name of the image file uploaded via discord commands.';
        COMMENT ON COLUMN emoji_list.created_at IS      'Date the emote was added to the guild.';
        COMMENT ON COLUMN emoji_list.uploader IS        'User id of the emoji uploader.';    
        """

    EXISTS_EMOJI_TABLE= "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE upper(table_name) = 'EMOJI_LIST');"

    UPDATE_EMOJI_NAME=  ""

    REMOVE_EMOJI=       "UPDATE public.emoji_list SET emoji_list.available = FALSE WHERE emoji_list.e_id = $1"

    ADD_EMOJI=          """                
                        INSERT INTO public.emoji_list(
                            e_id, name, animated, src_guild, src_image_name, created_at, uploader
                            )
                        VALUES(
                            $1, $2, $3, $4, $5, $6, $7
                            )
                        ON CONFLICT (e_id)
                            DO
                            UPDATE SET name = $2;
                        """

    GET_EMOJI_DUPE=     """     
                        SELECT emoji_list.e_id, emoji_list.name, emoji_list.animated, dups.row
                        FROM emoji_list
                        INNER JOIN (
                            SELECT 
                                name,
                                ROW_NUMBER() OVER(PARTITION BY name ORDER BY name ASC) AS Row
                            FROM emoji_list 
                            ) dups 
                        ON (emoji_list.name = dups.name AND dups.Row > 1)
                        ORDER BY name ASC;
                        """

  # ============================== VAULT TABLE ============================== 
    CREATE_VAULT_TABLE = """
        CREATE TABLE IF NOT EXISTS emoji_vault (
            e_id            BIGINT          PRIMARY KEY,
            name            VARCHAR(100)    NOT NULL,
            animated        BOOLEAN         NOT NULL,
            image           DISCORD_IMG,
            uploader        BIGINT,
            created_at      TIMESTAMP       DEFAULT TIMEZONE('utc'::text, NOW()),
            removed_at      TIMESTAMP       DEFAULT TIMEZONE('utc'::text, NOW()),
            src_guild       BIGINT,
            src_image_name  VARCHAR(100)
        );
    
        COMMENT ON TABLE emoji_vault IS                  'Holds information of all the emojis the bot can access. Storing this data would save bandwidth.';
        COMMENT ON COLUMN emoji_vault.e_id IS            'ID of the emote.';
        COMMENT ON COLUMN emoji_vault.name IS            'Emote name, the one it is called with.';
        COMMENT ON COLUMN emoji_vault.image IS           'Stored bytes of the emoji image. Stored here for the sake of the Vault.';
        COMMENT ON COLUMN emoji_vault.src_guild IS       'Guild the emoji is actually presant in.';
        COMMENT ON COLUMN emoji_vault.src_image_name IS  'Name of the image file uploaded via discord commands.';
        COMMENT ON COLUMN emoji_vault.created_at IS      'Date the emote was added to the guild.';
        COMMENT ON COLUMN emoji_vault.removed_at IS      'Date the emote was removed from the guild.';
        COMMENT ON COLUMN emoji_vault.uploader IS        'User id of the emoji uploader.';  
        """

    EXISTS_VAULT_TABLE= "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE upper(table_name) = 'EMOJI_VAULT');"

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


  # ============================== TRIGGERS ==============================
    EXISTS_EMOJIVAULT_TRIGGER="SELECT EXISTS(SELECT * FROM information_schema.triggers WHERE upper(trigger_name) = 'MANAGERETIREES');"

    CREATE_EMOJIVAULT_TRIGGER="""
        DO
        $do$
        BEGIN
        IF NOT EXISTS (SELECT * 
                FROM pg_proc
                WHERE prorettype <> 0 AND proname = 'emoji_manageRetirees' AND format_type(prorettype, NULL) = 'trigger') THEN

            CREATE OR REPLACE FUNCTION emoji_manageRetirees() RETURNS trigger
                LANGUAGE plpgsql
                COST 200 AS

            $$BEGIN
                IF OLD.vaultify = FLASE THEN
                    RETURN OLD;
                END IF;
                
                INSERT INTO public.emoji_vault(
                    e_id,  name, animated, image, uploader, created_at, removed_at, src_guild, src_image_name
                    )
                VALUES(
                    OLD.e_id,  OLD.name, OLD.animated, OLD.image, OLD.uploader, OLD.created_at, OLD.removed_at, OLD.src_guild, OLD.src_image_name
                    )
                ON CONFLICT (e_id)
                    DO NOTHING;

                RETURN OLD;
            END;$$;
        END IF;    

        IF NOT EXISTS(SELECT * FROM information_schema.triggers WHERE event_object_table = 'emoji_list' AND trigger_name = 'manageRetirees') THEN
            CREATE TRIGGER manageRetirees BEFORE DELETE ON emoji_list FOR EACH ROW
                EXECUTE PROCEDURE emoji_manageRetirees();
        END IF;
        END
        $do$
        """

  # ============================== COMPOUND DATATYPES ==============================
    EXISTS_DISCORD_IMG=       "SELECT EXISTS(SELECT * FROM pg_type WHERE typname='discord_img')"
    CREATE_DISCORD_IMG="""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'discord_img') THEN
                CREATE TYPE discord_img AS
                (
                emoji_ext       VARCHAR(10),
                emoji_img       BYTEA
                );
            END IF;
        END$$;

        COMMENT ON TYPE discord_img IS 'This Holds the bytes and extention for an image from discord.';
        """