from server_logic.definitions import UserIdentity
from db_models import User
import fsm.states as states

DUMMY_DB = {}


class Handler(object):
    STATES_HISTORY_LENGTH = 10

    def __init__(self):
        self.__start_state = "StartState"
        self.__states = {}
        self.__register_states(*states.collect())
        # Doesn't do anything for now, probably useless long-term
        # self.__commands = {
        #     '/start': "StartState",
        # }

    def __register_state(self, state_class):
        self.__states[state_class.__name__] = state_class()

    def __register_states(self, *states_):
        for state in states_:
            self.__register_state(state)

    def __get_state(self, name):
        if callable(name):
            name = name.__name__
        state = self.__states.get(name)
        if state is None:
            # If non-existing state - send user to the start state
            return False, self.__states[self.__start_state], self.__start_state
        return True, state, name

    async def __get_or_register_user(self, context):
        user_identity = UserIdentity(context['user_id'], context['service'])
        # DDOS protect
        if await self.__is_ddos(user_identity):
            return None
        # Using dummy db for now
        user = DUMMY_DB.get(user_identity.hash())
        if user is None:
            user = User(user_id=user_identity.user_id,
                        service=user_identity.service_in,
                        identity=user_identity.hash(),
                        first_name=context.get('first_name'),
                        last_name=context.get('last_name'),
                        username=context.get('username'))
            DUMMY_DB[user_identity.hash()] = {'user': user, 'states': []}
        else:
            user = user['user']
        await self.__register_event(user)
        return user

    async def __is_ddos(self, user_identity):
        # TODO: IMPLEMENT DDOS PROTECTION
        return False

    async def __register_event(self, user):
        # TODO: REGISTER USER ACTIVITY
        pass

    async def process(self, context):
        user = await self.__get_or_register_user(context)
        # Ddos protection triggered
        if user is None:
            return
        last_state = await self.last_state(user)
        correct_state, current_state, current_state_name = self.__get_state(last_state)
        if not correct_state:
            DUMMY_DB[user.identity]['states'].append(current_state_name)
        # Call process method of some state
        ret_code = await current_state.process(context, user)
        await self.__handle_ret_code(context, user, ret_code)

    # get last state of the user
    async def last_state(self, user):
        # defaults to __start_state
        try:
            return DUMMY_DB[user.identity]['states'][-1]
        except IndexError:
            return self.__start_state

    async def __handle_ret_code(self, context, user, ret_code):
        # Handle return codes
        if issubclass(ret_code, states.OK):
            return
        elif issubclass(ret_code, states.GO_TO_STATE):
            await self.__forward_to_state(context, user, ret_code.next_state)

    async def __forward_to_state(self, context, user, next_state):
        last_state = await self.last_state(user)
        correct_state, current_state, current_state_name = self.__get_state(next_state)
        DUMMY_DB[user.identity]['states'].append(current_state_name)
        # Check if history is too long
        if len(DUMMY_DB[user.identity]['states']):
            DUMMY_DB[user.identity]['states'].pop(0)
        if current_state.has_entry:
            ret_code = await current_state.entry(context, user)
        else:
            ret_code = await current_state.process(context, user)
        await self.__handle_ret_code(context, user, ret_code.next_state)