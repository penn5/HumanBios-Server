from . import base_state


class StartState(base_state.BaseState):
    has_entry = False

    async def process(self, context, user):
        print(context, user)
        return base_state.OK