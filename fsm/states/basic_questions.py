from strings import strings_text
from . import base_state


class BasicQuestionState(base_state.BaseState):
    async def entry(self, context, user, db):
        if user.current_state is None:
            user.current_state = "choose_lang"
        print(context, user)
        #await self.send('telegram', context, user)
        return base_state.OK

    async def process(self, context, user, db):
        #question = get_next_question(user.identity, user.language)
        #context['request']['message']['text'] = question.text
        # Temporary database
        #db[user.identity]['current_question'] = question

        #print(context, user, question)
        #await self.send('telegram', context, user)
        return base_state.OK