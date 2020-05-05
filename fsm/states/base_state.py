from db_models.conversations import ConversationDispatcher
from server_logic.definitions import Context, SenderTask
from settings import tokens, logger, ROOT_PATH
from translation import Translator
from aiohttp import ClientSession
from strings import strings_text
from db_models import User
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
    HEADERS = {
        "Content-Type": "application/json"
    }
    # This variable allows to ignore `entry()` when needed
    has_entry = True
    # All translations
    __STRINGS = strings_text
    # ALL languages
    LANGUAGES = strings_text.keys()
    # @Important: instantiate translator
    TRANSLATOR = Translator()
    # Media path and folder
    media_folder = "media"
    media_path = os.path.join(ROOT_PATH, media_folder)

    if not os.path.exists(media_path):
        os.mkdir(media_path)

    # @Important: instantiate conversations broker
    convo_broker = ConversationDispatcher()

    # Prepare state
    def __init__(self):
        # Keeps list of tasks
        self.tasks = dict()
        # Create language variable
        self.__language = 'en'

    @property
    def strings(self):
        """
        This property simplifies the access to strings

        Returns:
            dict: strings of the user language
        """
        return self.__STRINGS[self.__language]

    def set_language(self, value: str):
        """
        This method sets language to a current state
        If language is None - base language version is english

        Args:
            value (str): language code of the user's country
        """
        self.__language = value or "en"

    async def wrapped_entry(self, context, user, db):
        # Prepare language for state
        self.set_language(user.language)
        # Execute state method
        status = await self.entry(context, user, db)
        # Commit changes to database
        # user.save(), db.save(), etc

        # @Important: Since we call this always, check if
        # @Important: the call is actually needed
        if self.tasks.get(id(context)):
            # @Important: collect all requests
            _results = await self.collect(user, context)
        return status

    async def wrapped_process(self, context, user, db):
        # Prepare language for state
        self.set_language(user.language)
        # Execute state method
        status = await self.process(context, user, db)
        # Commit changes to database
        # user.save(), db.save(), etc

        # @Important: Since we call this always, check if
        # @Important: the call is actually needed
        if self.tasks.get(id(context)):
            # @Important: collect all requests
            _results = await self.collect(user, context)
        return status

    # Actual state method to be written for the state
    async def entry(self, context: Context, user: User, db):
        return OK

    # Actual state method to be written for the state
    async def process(self, context: Context, user: User, db):
        return OK

    # @Important: 1) find better way with database
    # @Important: 2) What if we do it in non blocking asyncio.create_task (?)
    # @Important:    But on the other hand, we can't relay on the file status
    # @Important:    for example if next call needs to upload it somewhere
    # @Important:    If you deal with reliability and consistency - great optimisation
    async def download_by_url(self, url, *folders, filename):
        # Make sure file exists
        if not self.exists(*folders):
            # Create folder on the path
            os.mkdir(os.path.join(self.media_path, *folders))
        # Full file path with filename
        filepath = os.path.join(self.media_path, *folders, filename)
        # Initiate aiohttp sessions, get file
        async with ClientSession() as session:
            async with session.get(url) as response:
                # Open file with aiofiles and start steaming bytes, write to the file
                async with aiofiles.open(filepath, 'wb') as f:
                    async for chunk in response.content.iter_any():
                        await f.write(chunk)
        return filepath

    # @Important: check if downloaded file exist
    def exists(self, *args):
        return os.path.exists(os.path.join(self.media_path, *args))

    # @Important: high level access to translation module
    # @Important: note, though, that we shouldn't abuse translation api
    # @Important: because a) it's not good enough, b) it takes time to make
    # @Important: a call to the google cloud api
    async def translate(self, target: str, text: str) -> str:
        return await self.TRANSLATOR.translate_text(target, text)

    # Sugar

    # @Important: command to actually send all collected requests from `process` or `entry`
    async def collect(self, user: User, context: Context):
        results = list()
        async with ClientSession() as session:
            # @Important: Since asyncio.gather order is not preserved, we don't want to run them concurrently
            # tasks = [self._send(task, session) for task in self.tasks[id(context)]]
            # group = asyncio.gather(*tasks)
            # results = await group
            # return results
            for each_task in self.tasks[id(context)]:
                res = await self._send(each_task, session)
                results.append(res)
            # @Important: Clear object after working with it
            del self.tasks[id(context)]
        return results

    # @Important: Real send method, takes SenderTask as argument
    async def _send(self, task: SenderTask, session: ClientSession):
        # Takes instance data holder object with the name from the tokens storage, extracts url
        url = tokens[task.user.via_instance].url
        # Unpack context, set headers (content-type: json)
        async with session.post(url, json=task.context.to_dict(), headers=self.HEADERS) as resp:
            # If reached server - log response
            if resp.status == 200:
                result = await resp.json()
                logger.info(f"Sending task status: {result}")
                return result
            # Otherwise - log error
            else:
                logger.info(f"[ERROR]: Sending task status {await resp.text()}")

    # @Important: `send` METHOD THAT ALLOWS TO SEND PAYLOAD TO THE USER
    def send(self, to_user: User, context: Context):
        # @Important: [Explanation to the code below]:
        # @Important: maybe add some queue of coroutines and dispatch them all when handler return OK (?)
        # @Important: or just dispatch them via asyncio.create_task so it will be more efficient (?)
        # @Important: reasoning:
        # @Important:   simple way:   server -> request1 -> status1 -> request2 -> status2 -> request3 -> status3
        # @Important:     this way:   server -> gather(request1, request2, request3) -> log(status1, status2, status3)

        if self.tasks.get(id(context)) is None:
            # @Important: 1) Using id() to provide completely unique key for the current `process` method
            # @Important: 2) Making deep copy of the object, because in different calls values will
            # @Important:    most surely be different, so we don't want to just pass pointer to the old object
            self.tasks[id(context)] = [SenderTask(to_user, context.deepcopy())]
        else:
            self.tasks[id(context)].append(SenderTask(to_user, context.deepcopy()))
