from server_logic.definitions import Context, SenderTask
from settings import tokens, logger, ROOT_PATH
from aiohttp import ClientSession
from strings import strings_text
from db_models import User
from copy import deepcopy
import aiofiles
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
        self.tasks = dict()
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

    async def wrapped_entry(self, context, user, db):
        result = await self.entry(context, user, db)
        # Commit changes to database
        # user.save(), db.save()
        # etc
        # @Important: collect all requests
        _results = await self.collect(user, context)
        return result

    async def wrapped_process(self, context, user, db):
        result = await self.process(context, user, db)
        # Commit changes to database
        # user.save(), db.save()
        # etc
        # @Important: collect all requests
        _results = await self.collect(user, context)
        return result

    async def entry(self, context, user, db):
        return OK

    async def process(self, context, user, db):
        return OK

    async def download_by_url(self, url, folder, filename):
        filepath = os.path.join(self.media_path, folder, filename)
        async with ClientSession() as session:
            async with session.get(url) as response:
                async for chunk, _ in response.content.iter_chunks():
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(chunk)
        return filepath

    def file_exists(self, *args):
        return os.path.exists(os.path.join(self.media_path, *args))

    # Sugar

    # @Important: command to actually send all collected requests from `process` or `entry`
    async def collect(self, user: User, context: Context):
        results = list()
        async with ClientSession() as session:
            # @Important: Since asyncio.gather order is not preserved, we don't want to run them simultaneously
            # tasks = [self._send(task, session) for task in self.tasks[id(context)]]
            # group = asyncio.gather(*tasks)
            # results = await group
            # return results
            for each_task in self.tasks[id(context)]:
                res = await self._send(each_task, session)
                results.append(res)
        return results

    async def _send(self, task: SenderTask, session: ClientSession):
        url = tokens[task.user.via_instance].url
        async with session.post(url, json=task.context.to_dict()) as resp:
            result = await resp.json()
            logger.info(f"Sending task status: {result}")
            return result

    # @Important: `send` METHOD THAT ALLOWS TO SEND PAYLOAD TO THE USER
    def send(self, to_user: User, context: Context):
        # @Important: maybe add some queue of coroutines and dispatch them all when handler return OK (?)
        # @Important: or just dispatch them via asyncio.create_task so it will be more efficient (?)
        # @Important: reasoning:
        # @Important:   simple way:   server -> request1 -> status1 -> request2 -> status2 -> request3 -> status3
        # @Important:     this way:   server -> gather(request1, request2, request3) -> log(status1, status2, status3)

        if self.tasks.get(to_user) is None:
            # Using id() to provide completely unique key for the current process method
            self.tasks[id(context)] = [SenderTask(to_user, deepcopy(context))]
        else:
            self.tasks[id(context)].append(SenderTask(to_user, deepcopy(context)))
