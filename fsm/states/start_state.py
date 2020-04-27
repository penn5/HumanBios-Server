from . import base_state


class StartState(base_state.BaseState):
    has_entry = False

    async def process(self, context, user):
        # TODO: LOG IN FOR MEDICS AND SOCIAL WORKERS
        #reference = context['request']['message']['text']

        return base_state.GO_TO_STATE("QuizState")