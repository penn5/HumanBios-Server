from settings import tokens, logger
import aiohttp
import asyncio


class OK:
    status = 1

    def __eq__(self, other):
        return self.status == other.status


class GO_TO_STATE:
    status = 2
    next_state = None

    def __init__(self, next_state):
        self.next_state = next_state

    def __eq__(self, other):
        return self.status == other.status


class BaseState(object):
    has_entry = True

    # Prepare state
    def __init__(self):
        self.tasks = list()

    async def entry(self, context, user, db):
        return OK
        #raise NotImplementedError("Please implement entry point for the state")

    async def process(self, context, user, db):
        return OK
        #raise NotImplementedError("Please implement event process method")

    async def send(self, service_out, user, context, url=None, headers=None):
        # There must be connection between users, bots and urls
        # e.g -> different tg bots, but user is mapped to his tg bot
        #if url is None:
        #    url = tokens[service_out].values()[0]

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=context.to_dict()) as resp:
                if not resp.status == 200:
                    logger.error(await resp.text())
                return resp

    # Sugar