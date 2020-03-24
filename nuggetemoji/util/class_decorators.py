import re 
import logging

from functools import wraps
from nuggetemoji.config import Config
from .misc import Response, _get_variable

config = Config()

def owner_only(func):
    @wraps(func)

    async def wrapper(self, *args, **kwargs):
        og_msg = _get_variable('message')

        print(og_msg)

        if (
            (og_msg)
            or (og_msg.author.id == config.owner_id)
            ):
            return await func(self, msg=og_msg)

        else:
            return await _responce_generator(self, content=f"`You are not the bot owner. Bot owner is <@{config.owner_id}>`")

    return wrapper

async def _responce_generator(self, content="", embed=None, reply=True, delete_after=None):
    return Response(content=content, embed=embed, reply=reply, delete_after=delete_after)
