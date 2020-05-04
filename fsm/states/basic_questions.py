from server_logic.definitions import Context
from db_models import User
from . import base_state

# TODO: Hardcoded order is bad (?), find a way to order everything
# TODO: in json file, much like covapp, so we will be able to change
# TODO: order/text/buttons etc via external api
# @Important: DONT CHANGE, IF CHANGED -> review all the code below AND in other states
ORDER = {
    1: "choose_lang", 2: "disclaimer", 3: "story", 4: "medical",
    5: "QA_TRIGGER", 6: "stressed", 7: "mental", 8: "wanna_help",
    9: "helping", 10: "location", 11: "selfie", 12: "coughing"
}


class BasicQuestionState(base_state.BaseState):

    async def entry(self, context: Context, user: User, db):
        if user.current_state is None:
            # @Important: Default starting state
            user.current_state = 1
            # @TMP: initiate resume, to record user answers
            db[user.identity]['resume'] = {}
            # Send language message
            context['request']['message']['text'] = self.strings["choose_lang"]
            context['request']['buttons_type'], context['request']['buttons'] = self.lang_keyboard()
            context['request']['has_buttons'] = True
            # Don't forget to send message
            self.send(user, context)
            return base_state.OK
        else:
            # If returning to the state from somewhere, with current_state -> continue
            # Send location message
            context['request']['message']['text'] = self.strings["location"]
            context['request']['has_buttons'] = False
            # Don't forget to send message
            self.send(user, context)
            return base_state.OK

    async def process(self, context, user: User, db):
        key = ORDER.get(user.current_state)
        # Raw text alias
        raw_text: str = context['request']['message']['text']

        # Dialog steps that require not trivial/free input
        free_answers = ["story", "helping", "location", "selfie", "coughing"]

        if key == "choose_lang":
            language = raw_text[5:]
            if language not in self.languages:
                context['request']['message']['text'] = self.strings["qa_error"]
                context['request']['buttons_type'], context['request']['buttons'] = self.lang_keyboard()
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
                # TODO: @Important: Need to keep private access, so we need static files server
                # TODO: @Important: that will create tokens and timestamps and allows time limited access
                db[user.identity]['resume']['selfie_path'] = path
            else:
                # @Important: bad value fallback
                common_buttons = [self.strings['yes'], self.strings['no'], self.strings['back']]
                if key not in free_answers and raw_text not in common_buttons:
                    # Tell user about invalid input
                    context['request']['message']['text'] = self.strings['qa_error']
                    self.send(user, context)
                    # Repeat the message
                    context['request']['message']['text'] = self.strings[key]
                    context['request']['buttons_type'], context['request']['buttons'] = self.simple_keyboard()
                    context['request']['has_buttons'] = True
                    self.send(user, context)
                    return base_state.OK
                # Make sure not to track `back` button
                if raw_text != self.strings['back']:
                    # TODO: Make sure to download links etc
                    # Record answer to the question
                    db[user.identity]['resume'][key] = context['request']['message']['text']

        # Conversation killers / Key points
        # Bonus value to skip one state
        bonus_value = 0
        # Denied disclaimer (or end of conv)
        if (key == "disclaimer" or key == "wanna_help") and raw_text == self.strings['no']:
            context['request']['message']['text'] = self.strings["bye"]
            context['request']['buttons'] = []
            context['request']['has_buttons'] = False
            self.send(user, context)
            # Don't need to change buttons, nothin changed
            context['request']['message']['text'] = self.strings["end_convo"]
            self.send(user, context)
            # Reset the flow
            user.current_state = None
            # Clear list of states related to the user
            db[user.identity]['states'].clear()
            return base_state.OK
        # if not medical -> jump to `stressed` question
        elif key == "medical" and raw_text == self.strings['no']:
            bonus_value = 1
        # if not stressed -> jump to `wanna_help`
        elif key == "stressed" and raw_text == self.strings['no']:
            bonus_value = 1
        # @Important: create social request
        elif key == "mental" and raw_text == self.strings['yes']:
            #donotrepeatyourcode
            return self.request_method(context, user, user.types.SOCIAL, "forward_shrink")
        # @Important: if coughing (last state) -> request doctor conversation
        elif key == "coughing":
            return self.request_method(context, user, user.types.MEDIC, "forward_doctor")
        elif key == "helping" and raw_text == self.strings['yes']:
            # TODO: Is not implemented yet
            ...

        # Back button
        if raw_text == self.strings['back']:
            user.current_state -= 1
        else:
            # Update current state
            user.current_state += 1 + bonus_value

        # Update current key
        key = ORDER.get(user.current_state)
        btn_type, buttons = self.simple_keyboard()
        # If key is in the free answers
        if key in free_answers:
            buttons = [{"text": self.strings['back']}]

        # @Important: Trigger different state to ask covapp QA
        if key == "QA_TRIGGER":
            return base_state.GO_TO_STATE("QAState")

        # Set values to the answer
        context['request']['message']['text'] = self.strings[key]
        context['request']['buttons'] = buttons
        context['request']['has_buttons'] = bool(buttons)
        context['request']['buttons_type'] = btn_type

        self.send(user, context)
        return base_state.OK

    # Buttons, according to schema

    def simple_keyboard(self):
        return "text", [
            {
                "text": self.strings['yes']
             },
            {
                "text": self.strings['no']
             },
            {
                "text": self.strings['back']
             }
        ]

    def lang_keyboard(self):
        return "inline", [
            {
                "text": key,
                "value": f"lang_{key}"
            }
            for key in self.languages
        ]

    def request_method(self, context, user: User, type_: User.types, forward_name: str):
        # request created
        self.convo_broker.request_conversation(user, user.types.SOCIAL)
        # Send user message, that the request was created
        context['request']['message']['text'] = self.strings[forward_name]
        self.send(user, context)
        # @Important: Don't change user's state. It will be changed when the conversation
        # @Important: will start, and both users are sent to the conversation state
        return base_state.GO_TO_STATE("AFKState")