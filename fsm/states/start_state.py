from . import base_state


class StartState(base_state.BaseState):
    has_entry = False

    async def process(self, context, user):
        text = context['text']
        context['text'] = f"Hello, {text.strip('/start ')}!"
        return base_state.OK