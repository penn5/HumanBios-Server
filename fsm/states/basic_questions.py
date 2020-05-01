from . import base_state


class BasicQuestionState(base_state.BaseState):
    async def entry(self, context, user, db):
        if user.current_state is None:
            user.current_state = "choose_lang"
        #
        #buttons = []
        #if user.current_state == "choose_lang":
        #    text = "Please select the language you want to me to talk in to you from now on."
        #    buttons = []
        #    user.current_state = "story"
        #elif user.current_state == "story":
        #    text = self.strings['story']
        #    user.current_state = "story"
        #elif user.current_state == "choose_lang":
        #    ...

        print(context, user)
        #await self.send(user, context)
        return base_state.OK

    async def process(self, context, user, db):
        #question = get_next_question(user.identity, user.language)
        #context['request']['message']['text'] = question.text
        # Temporary database
        #db[user.identity]['current_question'] = question

        #print(context, user, question)
        #await self.send('telegram', context, user)
        return base_state.OK