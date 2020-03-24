import re
from configparser import ConfigParser

from .util.exceptions import HelpfulError

class Config:
    def __init__(self):

        self.config_file = r'config/botConfig.ini'
        default_value = None

        config = ConfigParser(interpolation=None)
        config.read(self.config_file, encoding='utf-8')

        #confsections = {'Credentials', 'Bot', 'Roles', 'Guild', 'Giveaway'}.difference(config.sections())

        #if confsections:
        #    raise HelpfulError(
        #        "One or more required config sections are missing.",
        #        "Fix your config.  Each [Section] should be on its own line with "
        #        "nothing else on it.  The following sections are missing: {}".format(
        #            ', '.join(['[%s]' % s for s in confsections])
        #        ),
        #        preface="An error has occured parsing the config:\n"
        #    )

        self._confpreface = 'An error has occurred reading the config:\n'
        self._confpreface2 = 'An error has occured validating the config:\n'
        self.auth = ()

      # -------------------------------------------------- CREDENTIALS --------------------------------------------------
        self._login_token = config.get('Credentials', 'Token', fallback=ConfigDefaults.token)
        self.owner_id=      config.get('Credentials', 'Owner', fallback=ConfigDefaults.owner_id)

      # -------------------------------------------------- CHANNELS --------------------------------------------------
        self.channels = {}

        self.channels['bot_log']=                       config.getint( 'Channel', 'Bot Log',         fallback=default_value)
        self.channels['public_bot_log']=                config.getint( 'Channel', 'Public Bot Log',  fallback=default_value)
        self.channels['feedback_id']=                   config.getint( 'Channel', 'Feedback',        fallback=default_value)
        self.channels['reception_id']=                  config.getint( 'Channel', 'Reception',       fallback=default_value)


        self.channels['nugget_welcome_id']=             config.getint(  'Channel', 'Welcome MSG',    fallback=default_value)
        self.channels['entrance_gate']=                 config.getint(  'Channel', 'Entrance Gate',  fallback=default_value)
        self.channels['public_rules_id']=               config.getint(  'Channel', 'Public Rules',   fallback=default_value)

        self.run_checks()

    def run_checks(self):

        if not self._login_token:
            raise HelpfulError(
                'No bot token was specified in the config.',
                'Add one',
                preface=self._confpreface
            )

        else:
            self.auth = (self._login_token,)
class ConfigDefaults:
    #Bot owner
    owner_id = None

    token = None

    #bot
    command_prefix = '!'
    playing_game = ''
    delete_invoking = False


    #guild targetting
    target_guild_id = None
    servey_channel_id = None
    dyno_archive_id = None
    reception_id = None

    #Roles
    admin_role = 'Admin'
    mod_role = 'Moderator'
    tmod_role = 'Trainee'
    user_role = 'Core'
    newuser_role = 'Fresh'
