from server_logic.definitions import Context
from . import base_state
from db import User

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
        if user['context'].get("bq_state") == 10:
            # Send location message
            context['request']['message']['text'] = self.strings["location"]
            context['request']['has_buttons'] = True
            context['request']['buttons_type'] = "text"
            context['request']['buttons'] = [
                {"text": self.strings['skip']},
                {"text": self.strings['back']},
                {"text": self.strings['stop']}
            ]
            # Don't forget to add task
            self.send(user, context)
            return base_state.OK
            # If returning to the state from somewhere, with current_state -> continue
        elif user['context'].get("bq_state") == 4:
            # Send medical message
            context['request']['message']['text'] = self.strings["medical"]
            context['request']['has_buttons'] = True
            context['request']['buttons_type'], context['request']['buttons'] = self.simple_keyboard()
            # Don't forget to add task
            self.send(user, context)
            return base_state.OK
        elif user['context'].get("bq_state") == 1:
            # Send disclaimer message
            context['request']['message']['text'] = self.strings["disclaimer"]
            context['request']['has_buttons'] = True
            context['request']['buttons_type'] = "text"
            context['request']['buttons'] = [
                {"text": self.strings['accept']}, {"text": self.strings['reject']},
                {"text": self.strings['back']}, {"text": self.strings['stop']}
            ]
            user['context']['bq_state'] += 1
            # Don't forget to add task
            self.send(user, context)
            return base_state.OK
        else:
            # @Important: Default starting state
            user['context']['bq_state'] = 1
            return await self.process(context, user, db)

    async def process(self, context, user: User, db):
        # Take key associated with state
        key = ORDER.get(user['context']['bq_state'])
        # Raw text alias
        raw_text: str = context['request']['message']['text']
        button = self.parse_button(raw_text)        

        # Dialog steps that require non-trivial/free input
        free_answers = ["story", "helping", "location", "selfie", "coughing"]
        # If choose language (first) state
        if key == "choose_lang":
            return base_state.GO_TO_STATE("LanguageDetectionState")
        # Recording the answers, if skipped first two steps
        elif button != 'skip':
            # @Important: If user sends selfie - download the image
            if key == "selfie" and context['request']['has_image']:
                # TODO: Store all users input `properly`
                for index, each_file in enumerate(context['request']['files']):
                    url = each_file['payload']
                    # Download selfie to the user's folder
                    path = await self.download_by_url(url, f"'user_{user['identity']}'", filename=f'selfie_{index}.png')
                    # TODO: @Important: Serve files somehow to allow remote access via front ends
                    # TODO: @Important: Need to keep private access, so we need static files server that will
                    # TODO: @Important: create tokens and timestamps and allows time limited access to user data
                    # Save filepath to the user's resume
                    # If first element - set it as list, otherwise just append
                    if not index:
                        user['files']['selfie'] = [path]
                    else:
                        user['files']['selfie'].append(path)
            # @Important: If user sends voice not of them coughing - download the note
            elif key == "coughing" and context['request']['has_audio']:
                # Always will be only one voice note (per message)
                # TODO: Store all users input `properly`
                url = context['request']['files'][0]['payload']
                # Download voice note to the user's folder
                path = await self.download_by_url(url, f"user_{user['identity']}", filename='coughing.mp3')
                # Save filepath to the user's resume
                user['files']['cough_path'] = path
            # @Important: bad value fallback
            else:
                # Set of buttons, according user's language
                if key == "disclaimer":
                    common_buttons = ['accept', 'reject']
                else:
                    common_buttons = ['yes', 'no']
                # Add key buttons all the time
                common_buttons += ['back', 'stop']
                # Check if the question has strictly typed answer AND
                # it is one of the answers (buttons)
                if key not in free_answers and button not in common_buttons:
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
                if button not in ['back', 'stop']:
                    # TODO: Make sure to download links etc
                    # If current question is `location` -> save to the user data
                    if key == 'location':
                        user['last_location'] = raw_text
                    # Else record answer as a simple text
                    else:
                        # Record answer to the question
                        user['answers'][key] = context['request']['message']['text']

        # Conversation killers / Key points
        # Bonus value to skip one state
        bonus_value = 0
        # Denied disclaimer (or end of conv)
        if (key == "disclaimer" or key == "wanna_help") and button == 'reject':
            context['request']['message']['text'] = self.strings["bye"]
            context['request']['buttons'] = []
            context['request']['has_buttons'] = False
            self.send(user, context)
            # Don't need to change buttons, nothin changed
            context['request']['message']['text'] = self.strings["end_convo"]
            self.send(user, context)
            # Reset the flow
            user['context']['bq_state'] = 1
            # Clear list of states related to the user
            user['states'] = ["StartState"]
            return base_state.OK
        # if not medical -> jump to `stressed` question
        elif key == "medical" and button == 'no':
            # Add one to the state, so state will jump as we want (change in order will break it)
            bonus_value = 1
        # if not stressed -> jump to `wanna_help`
        elif key == "stressed" and button == 'no':
            bonus_value = 1
        # @Important: create social request
        elif key == "mental" and button == 'yes':
            #donotrepeatyourcode
            return self.request_method(context, user, db.types.SOCIAL, "forward_shrink")
        # @Important: if coughing (last state) -> request doctor conversation
        elif key == "coughing":
            return self.request_method(context, user, db.types.MEDIC, "forward_doctor")
        elif key == "helping" and button == 'yes':
            # TODO: Is not implemented yet
            return base_state.GO_TO_STATE("AFKState")

        # Back button
        if button == 'back':
            # Ensure jump from `location` -> `covapp QA`
            if key == "QA_TRIGGER":
                # Set to the qa state
                user['context']['bq_state'] = 5
            else:
                # else go one step back
                user['context']['bq_state'] -= 1
        # Stop button
        elif button == 'stop':
            # Jump from current state to final `end` state
            return base_state.GO_TO_STATE("ENDState")
        # TODO: Add conditional `skip` button
        else:
            # Update current state
            user['context']['bq_state'] += 1 + bonus_value

        # Update current key
        key = ORDER.get(user['context']['bq_state'])
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
        # @Important: If question is `disclaimer` - set special buttons
        elif key == "disclaimer":
            buttons = [{"text": self.strings['accept']}, {"text": self.strings['reject']},
                       {"text": self.strings['back']}, {"text": self.strings['stop']}]

        # Insert skip button
        if key in ["location", "selfie", "coughing"]:
            # Insert before back and stop buttons
            buttons.insert(len(buttons)-2, {"text": self.strings['skip']})

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
            for key in self.LANGUAGES
        ]

    # @Important: shortcut method for few actions
    def request_method(self, context, user: User, type_, forward_name: str):
        # request created
        # TODO: fix
        #  self.convo_broker.request_conversation(user, type_)
        # Send user message, that the request was created
        context['request']['message']['text'] = self.strings[forward_name]
        self.send(user, context)
        # @Important: Don't change user's state. It will be changed when the conversation
        # @Important: will start, and both users are sent to the conversation state
        return base_state.GO_TO_STATE("AFKState")
