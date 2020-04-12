from dataclasses import dataclass

@dataclass
class Guild:
    name: str
    id: int
    prefix: str = '?'
    channels: dict
    def __repr__(self):
        return "<Guild_Settings name={}, guild_id={}>".format(
            repr(self.name),
            self.id,
        )
        
    def get_channel(self, id):
        try:
             return self.channels[id]
        except KeyError:
            return None

    def set_webhook(self, ch_id, w_id, w_token):
        try:
            self.channels[ch_id].set_webhook(w_id, w_token)
        except KeyError:
            pass

    def get_webhook(self, ch_id):
        try:
            return self.channels[ch_id].get_webhook()
        except:
            return 0, 0


@dataclass
class Channel:
    id: int
    guild_id: int
    webhook_id: int
    webhook_token: str

    def get_webhook(self):
        return self.webhook_id, self.webhook_token

    def set_webhook(self, id, token):
        self.webhook_id = id
        self.webhook_token = token