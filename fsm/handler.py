from db_models import DataBase, User
from db_models import ServiceTypes
from settings import settings
import fsm.states as states


class Handler(object):
    STATES_HISTORY_LENGTH = 10

    def __init__(self):
        self.__start_state = "StartState"
        self.__states = {}
        self.__register_states(*states.collect())
        self.db = DataBase(settings.DATABASE_URL)

    def __register_state(self, state_class):
        self.__states[state_class.__name__] = state_class

    def __register_states(self, *states_):
        for state in states_:
            self.__register_state(state)

    def __get_state(self, name):
        if callable(name):
            name = name.__name__
        state = self.__states.get(name)
        if state is None:
            # If non-existing state - send user to the start state
            # @Important: Don't forget to initialize the state
            return False, self.__states[self.__start_state](), self.__start_state
        # @Important: Don't forget to initialize the state
        return True, state(), name

    async def __get_or_register_user(self, context):
        # Getting user from database
        user = await self.db.get_user(context['request']['user']['identity'])
        if user is None:
            user = {
                        "user_id": context['request']['user']['user_id'],
                        "service": context['request']['service_in'],
                        "identity": context['request']['user']['identity'],
                        "via_instance": context['request']['via_instance'],
                        "first_name": context['request']['user']['first_name'],
                        "last_name": context['request']['user']['last_name'],
                        "username": context['request']['user']['username'],
                        "language": 'en',
                        "type": self.db.types.COMMON,
                        "created_at": self.db.now().isoformat(),
                        "last_location": None,
                        "last_active": self.db.now().isoformat(),
                        "conversation_id": None,
                        "answers": dict(),
                        "files": dict(),
                        "states": list(),
                        "context": dict()
                    }
            await self.db.create_user(user)

        # @Important: Dynamically update associated service instance, when it was changed
        if context['request']['via_instance'] != user["via_instance"]:
            # Update database
            user = await self.db.update_user(
                user,
                "SET via_instance = :v",
                {":v": context['request']['via_instance']}
            )

        await self.__register_event(user)
        return user

    async def __register_event(self, user: User):
        # TODO: REGISTER USER ACTIVITY
        pass

    async def process(self, context):
        # Getting or registering user
        user = await self.__get_or_register_user(context)
        # Finding last registered state of the user
        last_state = await self.last_state(user, context)
        # Looking for state, creating state object
        correct_state, current_state, current_state_name = self.__get_state(last_state)
        if not correct_state:
            # Registering new last state
            user = await self.db.update_user(
                user,
                "SET states = list_append(states, :i)",
                {":i": [current_state_name]}
            )
        # Call process method of some state
        ret_code = await current_state.wrapped_process(context, user, self.db)
        await self.__handle_ret_code(context, user, ret_code)

    # get last state of the user
    async def last_state(self, user: User, context):
        # special cases #
        # TELEGRAM SPECIAL CASES
        if context['request']['service_in'] == ServiceTypes.TELEGRAM:
            text = context['request']['message']['text']
            if text and text.startswith("/start"):
                context['request']['message']['text'] = text[6:].strip()
                return self.__start_state
        # defaults to __start_state
        try:
            return user['states'][-1]
        except IndexError:
            return self.__start_state

    async def __handle_ret_code(self, context, user, ret_code):
        # Handle return codes
        #    If status is OK -> Done
        #    If status is GO_TO_STATE -> proceed executing wanted state
        if ret_code == states.OK:
            return
        elif isinstance(ret_code, states.GO_TO_STATE):
            await self.__forward_to_state(context, user, ret_code.next_state)

    async def __forward_to_state(self, context, user, next_state):
        last_state = await self.last_state(user, context)
        correct_state, current_state, current_state_name = self.__get_state(next_state)
        # Registering new last state
        user = await self.db.update_user(
            user,
            "SET states = list_append(states, :i)",
            {":i": [current_state_name]}
        )
        # Check if history is too long
        if len(user['states']) > self.STATES_HISTORY_LENGTH:
            user = await self.db.update_user(user, "REMOVE states[0]", None)

        if current_state.has_entry:
            ret_code = await current_state.wrapped_entry(context, user, self.db)
        else:
            ret_code = await current_state.wrapped_process(context, user, self.db)
        await self.__handle_ret_code(context, user, ret_code)