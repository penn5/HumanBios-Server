from . import base_state
from qa_module import get_next_question


class QuizState(base_state.BaseState):
    has_entry = False

    async def entry(self, context, user):
        context['request']['message']['text'] = "I will ask you some questions"
        await self.send('telegram', context, user)
        return base_state.OK

    async def process(self, context, user):
        context['request']['message']['text'] = get_next_question(user.identity, 'en')
        await self.send('telegram', context, user)
        return base_state.OK