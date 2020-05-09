from server_logic.definitions import Context
from db_models import User
from . import base_state


class AFKState(base_state.BaseState):
    has_entry = False

    # TODO: @TMP: This method probably shouldn't be here when everything else works properly (AKA On Release)
    async def process(self, context: Context, user: User, db):
        # Reset the flow
        db.current_states[user['identity']] = None
        # Set user to the start state
        user['states'] = ["StartState"]
        return base_state.OK
