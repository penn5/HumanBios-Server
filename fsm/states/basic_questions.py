from server_logic.definitions import Context
from db_models import User
from . import base_state

# TODO: Hardcoded order is bad (?), find a way to order everything
# TODO: in json file, much like covapp, so we will be able to change
# TODO: order/text/buttons etc via external api
ORDER = {
    1: "choose_lang", 2: "disclaimer", 3: "story", 4: "medical",
    5: "QA_TRIGGER", 6: "stressed", 7: "mental", 8: "wanna_help",
    9: "helping", 10: "bye", 11: "location", 12: "selfie",
    13: "coughing", 14: "forward_doctor"
}


class BasicQuestionState(base_state.BaseState):

    async def entry(self, context: Context, user: User, db):
        # @Important: Default starting state
        user.current_state = 1
        # @TMP: initiate resume, to record user answers
        db[user.identity]['resume'] = {}
        # Send language message
        context['request']['message']['text'] = self.strings["choose_lang"]
        context['request']['buttons'] = self.lang_keyboard()
        context['request']['has_buttons'] = True
        # Don't forget to send message
        self.send(user, context)
        return base_state.OK

    async def process(self, context, user, db):
        key = ORDER.get(user.current_state)
        # Raw text alias
        raw_text: str = context['request']['message']['text']

        if key == "choose_lang":
            language = raw_text[5:]
            if language not in self.languages:
                context['request']['message']['text'] = self.strings["qa_error"]
                context['request']['buttons'] = self.lang_keyboard()
                context['request']['has_buttons'] = True
                # Don't forget to send message
                self.send(user, context)
                return base_state.OK
            else:
                user.language = language
                self.set_language(user.language)
        # Recording the answers
        elif user.current_state > 2:
            # @Important: If user sends selfie - download the image
            if key == "selfie" and context['request']['has_image']:
                # Should be only one selfie picture
                url = context['request']['files'][0]['payload']
                # Download selfie in the user's folder
                path = await self.download_by_url(url, f'user_{user.identity}', 'selfie.png')
                # TODO: Serve files somehow to allow remote access via front ends
                db[user.identity]['resume'] = path
            else:
                # @Important: bad value fallback
                if key != "story" and raw_text not in [self.strings['yes'], self.strings['no'], self.strings['back']]:
                    # Tell user about invalid input
                    context['request']['message']['text'] = self.strings['qa_error']
                    self.send(user, context)
                    # Repeat the message
                    context['request']['message']['text'] = self.strings[key]
                    context['request']['buttons'] = self.simple_keyboard()
                    context['request']['has_buttons'] = True
                    self.send(user, context)
                    return base_state.OK
                # Record answer to the question
                db[user.identity]['resume'][key] = context['request']['message']['text']

        # Conversation killers / Key points
        # Denied disclaimer
        if key == "disclaimer" and raw_text == self.strings['no']:
            context['request']['message']['text'] = self.strings["bye"]
            context['request']['buttons'] = []
            context['request']['has_buttons'] = False
            self.send(user, context)
            # Don't need to change buttons, nothin changed
            context['request']['message']['text'] = self.strings["end_convo"]
            self.send(user, context)
            # Reset the flow
            user.current_state = None
            return base_state.OK

        # Back button
        if raw_text == self.strings['back']:
            user.current_state -= 2
        else:
            # Update current state
            user.current_state += 1
        # Update current key
        key = ORDER.get(user.current_state)

        if key == "story":
            buttons = []
        else:
            buttons = self.simple_keyboard()

        # @Important: Trigger different state to ask QA
        if key == "QA_TRIGGER":
            return base_state.GO_TO_STATE("QAState")

        # Set values to the answer
        context['request']['message']['text'] = self.strings[key]
        context['request']['buttons'] = buttons
        context['request']['has_buttons'] = bool(buttons)

        self.send(user, context)
        return base_state.OK

    # Buttons, according to schema

    def simple_keyboard(self):
        return [
            {
                "type": "text",
                "text": self.strings['yes']
             },
            {
                "type": "text",
                "text": self.strings['no']
             },
            {
                "type": "text",
                "text": self.strings['back']
             }
        ]

    def lang_keyboard(self):
        return [
            {
                "type": "inline",
                "text": key,
                "value": f"lang_{key}"
            }
            for key in self.languages
        ]