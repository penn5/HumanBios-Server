from server_logic.definitions import Context
from db_models import User
from . import base_state

# TODO: Hardcoded order is bad (?), find a way to order everything
# TODO: in json file, much like covapp, so we will be able to change
# TODO: order/text/buttons etc via external api
# TODO: But, of course, all that makes no sense, because there is a lot of code
# TODO: that depends on the order, and a lot of new code has to be inserted in case of change
# @Important: DONT CHANGE, IF CHANGED -> review all the code below AND in other states
ORDER = {
    1: "choose_lang", 2: "disclaimer", 3: "story", 4: "medical",
    5: "QA_TRIGGER", 6: "stressed", 7: "mental", 8: "wanna_help",
    9: "helping", 10: "location", 11: "selfie", 12: "coughing"
}


class BasicQuestionState(base_state.BaseState):

    async def entry(self, context: Context, user: User, db):
        # If returning to the state from somewhere, with current_state -> continue
        if user.current_state == 10:
            # Send location message
            context['request']['message']['text'] = self.strings["location"]
            context['request']['has_buttons'] = False
            # Don't forget to add task
            self.send(user, context)
            return base_state.OK
        else:
            # @Important: Default starting state
            user.current_state = 1
            # @TMP: initiate resume, to record user answers
            db[user.identity]['resume'] = {}
            # Send language message
            context['request']['message']['text'] = self.strings["choose_lang"]
            context['request']['buttons_type'], context['request']['buttons'] = self.lang_keyboard()
            context['request']['has_buttons'] = True
            # Don't forget to add task
            self.send(user, context)
            return base_state.OK

    async def process(self, context, user: User, db):
        # Take key associated with state
        key = ORDER.get(user.current_state)
        # Raw text alias
        raw_text: str = context['request']['message']['text']

        # Dialog steps that require non-trivial/free input
        free_answers = ["story", "helping", "location", "selfie", "coughing"]
        # If choose language (first) state
        if key == "choose_lang":
            # Cut data to extract language (e.g. `lang-en` -> `en`)
            # TODO: 1) Change language buttons data to avoid cutting, make them just `en` etc
            # TODO: 2) Due to current implementation on the front-end (see 1), raises NonType error
            # TODO:    when users enters invalid input with inline buttons
            # TODO: @Important: Also, make sure user input is not too short to break the code
            try:
                language = raw_text[5:]
            except:
                language = ""
            # If user input is not in the languages -> return error message
            if language not in self.languages:
                context['request']['message']['text'] = self.strings["qa_error"]
                context['request']['buttons_type'], context['request']['buttons'] = self.lang_keyboard()
                context['request']['has_buttons'] = True
                # Don't forget to add task
                self.send(user, context)
                return base_state.OK
            else:
                # If legit language -> save language to the user
                user.language = language
                # @Important: And set current context to the new language
                # @Important: (Will be done automatically with the next event)
                self.set_language(user.language)
        # Recording the answers, if skipped first two steps
        else:
            # @Important: If user sends selfie - download the image
            if key == "selfie" and context['request']['has_image']:
                # Should be only one selfie picture
                # TODO: Store all users input
                url = context['request']['files'][0]['payload']
                # Download selfie in the user's folder
                path = await self.download_by_url(url, f'user_{user.identity}', 'selfie.png')
                # TODO: @Important: Serve files somehow to allow remote access via front ends
                # TODO: @Important: Need to keep private access, so we need static files server that will
                # TODO: @Important: create tokens and timestamps and allows time limited access to user data
                # Save filepath to the user's resume
                db[user.identity]['resume']['selfie_path'] = path
            # @Important: bad value fallback
            else:
                # Set of buttons, according user's language
                common_buttons = [self.strings['yes'], self.strings['no'], self.strings['back'], self.strings['stop']]
                # Check if the question has strictly typed answer AND
                # it is one of the answers (buttons)
                if key not in free_answers and raw_text not in common_buttons:
                    # Tell user about invalid input
                    context['request']['message']['text'] = self.strings['qa_error']
                    self.send(user, context)
                    # Repeat the question message
                    context['request']['message']['text'] = self.strings[key]
                    context['request']['buttons_type'], context['request']['buttons'] = self.simple_keyboard()
                    context['request']['has_buttons'] = True
                    self.send(user, context)
                    return base_state.OK
                # @Important: tracking (saving) user input
                # Make sure not to track `back` button
                if raw_text not in [self.strings['back'], self.strings['stop']]:
                    # TODO: Make sure to download links etc
                    # If current question is `location` -> save to the user data
                    if key == 'location':
                        user.last_location = raw_text
                    # Else record answer as a simple text
                    else:
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
            # Add one to the state, so state will jump as we want (change in order will break it)
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
            return base_state.GO_TO_STATE("AFKState")

        # Back button
        if raw_text == self.strings['back']:
            # Ensure jump from `location` -> `covapp QA`
            if key == "QA_TRIGGER":
                # Set to the qa state
                user.current_state = 5
            else:
                # else go one step back
                user.current_state -= 1
        # Stop button
        elif raw_text == self.strings['stop']:
            # Jump from current state to final `end` state
            return base_state.GO_TO_STATE("ENDState")
        # TODO: Add conditional `skip` button
        else:
            # Update current state
            user.current_state += 1 + bonus_value

        # Update current key
        key = ORDER.get(user.current_state)
        # Get button type and yes/no/back keyboard
        btn_type, buttons = self.simple_keyboard()
        # If key is in the free answers -> remove keyboard
        if key in free_answers:
            # Leave only `back` and  button
            buttons = [{"text": self.strings['back']}, {"text": self.strings['stop']}]
        # @Important: If user presses `back` button and returns to the language -
        # @Important: set buttons to the language names (edge case)
        elif key == "choose_lang":
            # Change also button type to inline
            btn_type, buttons = self.lang_keyboard()

        # @Important: Trigger different state to ask covapp QA
        if key == "QA_TRIGGER":
            # Go to the qa state `entry()` instead
            return base_state.GO_TO_STATE("QAState")

        # Prepare values of the `answer request`
        context['request']['message']['text'] = self.strings[key]
        context['request']['buttons'] = buttons
        context['request']['has_buttons'] = bool(buttons)
        context['request']['buttons_type'] = btn_type

        self.send(user, context)
        return base_state.OK

    # Buttons, according to schema

    # Three buttons in the row
    # TODO: Change schema to accept matrix of buttons instead of list
    # TODO: (We want to be able to prepare 2D matrix of buttons, for
    # TODO: services like facebook, we then should unpack them into one row)
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
             },
            {
                "text": self.strings['stop']
            }
        ]

    # Buttons of all possible languages
    # TODO: Also make sure to make them into proper 2D matrix
    def lang_keyboard(self):
        return "inline", [
            {
                "text": key,
                "value": f"lang_{key}"
            }
            for key in self.languages
        ]

    # @Important: shortcut method for few actions
    def request_method(self, context, user: User, type_: User.types, forward_name: str):
        # request created
        self.convo_broker.request_conversation(user, user.types.SOCIAL)
        # Send user message, that the request was created
        context['request']['message']['text'] = self.strings[forward_name]
        self.send(user, context)
        # @Important: Don't change user's state. It will be changed when the conversation
        # @Important: will start, and both users are sent to the conversation state
        return base_state.GO_TO_STATE("AFKState")