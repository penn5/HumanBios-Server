from . import base_state

# TODO: Hardcoded order is bad (?), find a way to order everything
# TODO: in json file, much like covapp, so we will be able to change
# TODO: order/text/buttons etc via external api
ORDER = {
    1: "choose_lang", 2: "disclaimer", 3: "story", 4: "selfie",
    5: "disclaimer", 6: "medical", 7: "stressed", 8: "mental",
    9: "QA_TRIGGER", 10: "coughing", 11: "location"
}


class BasicQuestionState(base_state.BaseState):
    has_entry = False

    async def process(self, context, user, db):
        # @Important: Default starting state
        if user.current_state is None:
            user.current_state = 1
            # @TMP: initiate resume, to record user answers
            db[user.identity]['resume'] = {}

        # @Important: Trigger different state to ask QA
        if ORDER.get(user.current_state) == "QA_TRIGGER":
            return base_state.GO_TO_STATE("QAState")

        key = ORDER.get(user.current_state)
        # Buttons
        if key == "choose_lang":
            buttons = self.lang_keyboard()
        elif key == "story":
            buttons = []
        else:
            buttons = self.simple_keyboard()
        # @Important: Next state after lang, so assign user language here
        if key == "disclaimer":
            # Extract language code
            raw_text: str = context['request']['message']['text']
            language = raw_text.strip("lang_")
            # If language is not valid - resend the message
            if language not in self.languages:
                context['request']['message']['text'] = self.strings["choose_lang_fallback"]
                context['request']['buttons'] = self.lang_keyboard()
                context['request']['has_buttons'] = bool(buttons)
                # Don't forget to send message
                self.send(user, context)
                return base_state.OK
            user.language = language

        # Recording the answers
        if user.current_state > 2:
            # @Important: If user sends selfie - download the image
            if key == "selfie" and context['request']['has_image']:
                # Should be only one selfie picture
                url = context['request']['files'][0]['payload']
                # Download selfie in the user's folder
                path = await self.download_by_url(url, f'user_{user.identity}', 'selfie.png')
                # TODO: Serve files somehow to allow remote access via front ends
                db[user.identity]['resume'] = path
            else:
                # TODO: Make sure user entered proper answer (used buttons, etc)
                # Record answer to the question
                db[user.identity]['resume'] = context['request']['message']['text']

        # Set values to the answer
        context['request']['message']['text'] = self.strings[key]
        context['request']['buttons'] = buttons
        context['request']['has_buttons'] = bool(buttons)
        # Update current state
        user.current_state += 1

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