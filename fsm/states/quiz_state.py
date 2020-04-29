from . import base_state
from qa_module import get_next_question


class QuizState(base_state.BaseState):
    async def entry(self, context, user, db):
        context['request']['message']['text'] = "I will ask you some questions"
        print(context, user)
        #await self.send('telegram', context, user)
        return base_state.OK

    async def process(self, context, user, db):
        question = get_next_question(user.identity, 'en')
        context['request']['message']['text'] = question.text
        # Buttons
        #context['request']['message'][''] = question.text

        print(context, user)
        #await self.send('telegram', context, user)
        return base_state.OK