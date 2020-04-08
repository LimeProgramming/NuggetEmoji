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
        self._login_token =     config.get(         'Credentials', 'Token',           fallback=ConfigDefaults.token)
        self.owner_id=          config.getint(      'Credentials', 'Owner',           fallback=ConfigDefaults.owner_id)

      # -------------------------------------------------- BOT --------------------------------------------------
        self.delete_invoking=   config.getboolean(  'Bot',        'DeleteInvoking',    fallback=ConfigDefaults.delete_invoking)
        self.command_prefix=    config.get(         'Bot',        'command_prefix',    fallback=ConfigDefaults.command_prefix)
        self.playing_game=      config.get(         'Bot',        'game',              fallback=ConfigDefaults.playing_game)
        
      # -------------------------------------------------- DATABASE --------------------------------------------------

        self.use_sqlite=        config.getboolean(  'Database',   'SQLite',           fallback=True)
        self.use_postgre=       config.getboolean(  'Database',   'PostgreSQL',       fallback=False)

        self.pg_login = {}

        self.pg_login['host']=  config.get(         'PostgreSQL', 'Host',             fallback=default_value)
        self.pg_login['name']=  config.get(         'PostgreSQL', 'Database Name',    fallback=default_value)
        self.pg_login['user']=  config.get(         'PostgreSQL', 'User',             fallback=default_value)
        self.pg_login['pwrd']=  config.get(         'PostgreSQL', 'Password',         fallback=default_value)

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

      # ---------- Default to use sqlite
        if not self.use_postgre and not self.use_sqlite:
          self.use_sqlite = True

        if self.use_sqlite and self.use_postgre:
          raise HelpfulError(
            'Both SQLite and PostgreSQL are set to be used in config.ini',
            'Bot cannot use both services, please select only one.',
            preface=self._confpreface
          )

      # ---------- Make sure theres postgre login info
        if self.use_postgre:
          if not all(self.pg_login.values()):
            raise HelpfulError(
              'Not all PostgreSQL login infomation was provided.',
              'If PostgreSQL is desired please fill in the required login information for the PostgreSQL server or else use SQLite.',
              preface=self._confpreface
            )
          
          # ---------- Clean up login info
          for x in self.pg_login:
            self.pg_login[x] = self.pg_login[x].replace("'", "").replace("\"", "")



class ConfigDefaults:
    #Bot owner
    owner_id = None

    token = None

    #bot
    command_prefix = '!'
    playing_game = ''
    delete_invoking = False