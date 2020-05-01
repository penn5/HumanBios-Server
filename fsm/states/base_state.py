from settings import tokens, logger, ROOT_PATH
from strings import strings_text
import aiofiles
import aiohttp
import asyncio
import os


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
        self.media_folder = "media"
        self.media_path = os.path.join(ROOT_PATH, self.media_folder)

        if not os.path.exists(self.media_path):
            os.mkdir(self.media_path)

        # @Important: easy way to access all string tokens
        self.__strings = strings_text
        self.__language = 'en'

    # Getter method for strings, that gives string prepared in user's language
    @property
    def strings(self):
        return self.__strings[self.__language]

    def set_language(self, value):
        self.__language = value

    async def entry(self, context, user, db):
        return OK
        #raise NotImplementedError("Please implement entry point for the state")

    async def process(self, context, user, db):
        return OK
        #raise NotImplementedError("Please implement event process method")

    async def download_by_url(self, url, folder, filename):
        filepath = os.path.join(self.media_path, folder, filename)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                async for chunk, _ in response.content.iter_chunks():
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(chunk)
        return filepath

    def file_exists(self, *args):
        return os.path.exists(os.path.join(self.media_path, *args))

    # Sugar

    # TODO: `send` METHOD THAT ALLOWS TO SEND PAYLOAD TO THE USER VIA HIGH LEVEL METHOD
    async def send(self):
        # TODO: maybe add some queue of coroutines and dispatch them all when handler return OK (?)
        # TODO: or just dispatch them via asyncio.create_task so we will be more efficient (?)
        # TODO: reasoning:
        # TODO:         1st way:   server -> request1 -> status1 -> request2 -> status2 -> request3 -> status3
        # TODO:         2nd way:   server -> gather(request1, request2, request3) -> log(status1, status2, status3)
        pass
