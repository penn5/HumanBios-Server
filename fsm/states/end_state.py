from server_logic.definitions import Context
from db_models import User
from . import base_state


class ENDState(base_state.BaseState):
    has_entry = False

    # @Important: This state purposely resets whole dialog
    async def process(self, context: Context, user: User, db):
        # End conversation message, no buttons
        context['request']['message']['text'] = self.strings["end_convo"]
        context['request']['has_buttons'] = False
        self.send(user, context)
        # Reset the flow
        db.set_state(user, 1)
        # Clear list of states related to the user
        user['states'] = ['StartState']
        # The next message from user will trigger StartState
        return base_state.OK