import discord 

class _FakeBool:
    def __repr__(self):
        return 'True'

    def __eq__(self, other):
        return other is True

    def __bool__(self):
        return True

default = _FakeBool()

class AllowedMentions:

    __slots__ = ('everyone', 'users', 'roles')

    def __init__(self, *, everyone=default, users=default, roles=default):
        self.everyone = everyone
        self.users = users
        self.roles = roles

    def to_dict(self):
        parse = []
        data = {}

        if self.everyone:
            parse.append('everyone')

      # ---------- Sort Out Users
        if self.users == True:
            parse.append('users')

        elif self.users != False:
            data['users'] = list()

            for x in self.users:
                if isinstance(x, discord.User):
                    data['users'].append(x.id)

                elif type(x) is int:
                    data['users'].append(x)
                
                elif type(x) is str:
                    data['users'].append(int(x))

      # ---------- Sort Out Roles
        if self.roles == True:
            parse.append('roles')

        elif self.roles != False:
            data['roles'] = []

            for x in self.roles:
                if isinstance(x, discord.Role):
                    data['roles'].append(x.id)

                elif type(x) is int:
                    data['roles'].append(x)

                elif type(x) is str:
                    data['roles'].append(int(x))

      # ---------- Sort Out Parse
        data['parse'] = parse

        return data

    def merge(self, other):
        # Creates a new AllowedMentions by merging from another one.
        # Merge is done by using the 'self' values unless explicitly
        # overridden by the 'other' values.
        everyone = self.everyone if other.everyone is default else other.everyone
        users = self.users if other.users is default else other.users
        roles = self.roles if other.roles is default else other.roles
        return AllowedMentions(everyone=everyone, roles=roles, users=users)