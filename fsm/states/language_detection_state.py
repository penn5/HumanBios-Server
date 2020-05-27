from server_logic.definitions import Context
from db import User
from . import base_state
import logging


class LanguageDetectionState(base_state.BaseState):

    async def entry(self, context: Context, user: User, db):
        # Send language message
        context['request']['message']['text'] = self.strings["choose_lang"]
        # Set user context as 'Was Asked Language Question'
        user['context']['language_state'] = 1
        # Don't forget to add task
        self.send(user, context)
        return base_state.OK

    # @Important: This state purposely resets whole dialog
    async def process(self, context: Context, user: User, db):
        raw_answer = context['request']['message']['text']
        failed = True
        button = self.parse_button(raw_answer)

        if button == 'stop':
            # Jump from current state to final `end` state
            return base_state.GO_TO_STATE("ENDState")

        if user['context'].get('language_state') == 1:
            # Run language detection
            language_obj = await self.nlu.detect_language(raw_answer)
            # Couldn't detect any language
            if language_obj is None:
                # Ask if user wants to continue with the language
                context['request']['message']['text'] = self.strings["failed_language"].format(raw_answer)
                context['request']['has_buttons'] = True
                context['request']['buttons_type'] = "text"
                context['request']['buttons'] = [
                    {"text": self.strings['stop']}
                ]
                self.send(user, context)
                return base_state.OK

            # Update current context
            user['language'] = language_obj['iso639_1']
            self.set_language(language_obj['iso639_1'])

            # Ask if user wants to continue with the language
            context['request']['message']['text'] = self.strings["confirm_language"].format(language_obj['native'])
            context['request']['has_buttons'] = True
            context['request']['buttons_type'] = "text"
            context['request']['buttons'] = [
                {"text": self.strings['continue']},
                {"text": self.strings['try_again']},
                {"text": self.strings['stop']}
            ]
            user['context']['language_state'] = 2
            self.send(user, context)
            return base_state.OK

        elif user['context'].get('language_state') == 2:
            if button == 'continue':
                return base_state.GO_TO_STATE("BasicQuestionState")
            elif button == 'try_again':
                failed = False
                user['language'] = 'en'
                self.set_language('en')
                

        if failed:
            # Failed to recognise the answer -> fail message path
            context['request']['message']['text'] = self.strings["invalid_answer"]
            self.send(user, context)
        # Send language message, but now with "Stop" button
        context['request']['message']['text'] = self.strings["choose_lang"]
        context['request']['has_buttons'] = True
        context['request']['buttons_type'] = "text"
        context['request']['buttons'] = [
            {"text": self.strings['stop']}
        ]
        # Set user context as 'Was Asked Language Question'
        user['context']['language_state'] = 1
        # Don't forget to add task
        self.send(user, context)
        return base_state.OK
