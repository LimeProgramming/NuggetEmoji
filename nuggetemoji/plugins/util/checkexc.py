import discord 

class CustomCheckFailure(discord.ext.commands.CommandError):
    """Exception raised when the predicates in :attr:`.Command.checks` have failed.
    This inherits from :exc:`CommandError`
    """
    pass

# -------------------- EXCEPTIONS --------------------
class MissingPermissions(CustomCheckFailure):
    """
    Exception raised when the command invoker lacks permissions to run a
    command.
    This inherits from :exc:`CheckFailure`
    Attributes
    -----------
    missing_perms: :class:`list`
        The required permissions that are missing.
    """

    def __init__(self, missing_perms, embed=None):

        self.missing_perms = missing_perms

        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in missing_perms]

        if len(missing) > 2:
            fmt = '{}, and {}'.format(", ".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        message = 'You are missing {} permission(s) to run this command.'.format(fmt)

        super().__init__(message, embed)
        
        self._message = message
        self._embed = embed

    @property
    def message(self):
        return self._message

    @property
    def embed(self):
        return self._embed
