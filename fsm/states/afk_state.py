from server_logic.definitions import Context
from db_models import User
from . import base_state


class AFKState(base_state.BaseState):
    has_entry = False

    # TODO: @TMP: Shouldn't be here when everything else works properly (AKA On Release)
    async def process(self, context: Context, user: User, db):
        # Reset the flow
        user.current_state = None
        # Clear list of states related to the user
        db[user.identity]['states'].clear()
        return base_state.OK
