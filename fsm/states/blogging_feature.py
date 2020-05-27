from . import base_state
from server_logic.definitions import Context
from db import User

ORDER = {
    1: "choose_lang", 2: "disclaimer", 3: "story", 4: "medical",
    5: "QA_TRIGGER", 6: "stressed", 7: "mental", 8: "wanna_help",
    9: "helping", 10: "location", 11: "selfie", 12: "coughing"
}


class BloggingState(base_state.BaseState):
    has_entry = False

    async def process(self, context: Context, user: User, db):

        if "blogging" not in user["context"]:
            user["context"]["blogging"] = "start"
            user["context"]["blogging_state"] = user["states"][-1]
            return base_state.GO_TO_STATE("BloggingState")
        if user["context"]["blogging"] == "start":
            user["context"]["blogging"] = "edit"
            # test
            context['request']['message']['text'] = self.strings["edit_story"] + user['answers']["story"]
            context['request']['buttons_type'] = "text"
            context['request']['buttons'] = [
                {"text": self.strings['edit']},
                {"text": self.strings['pass']},
                {"text": self.strings['stop']}
            ]
            # Don't forget to add task
            self.send(user, context)
            return base_state.OK
        if user["context"]["blogging"] == "edit":
            if context['request']['message']['text'] == self.strings['edit']:
                context['request']['message']['text'] = self.strings["edit_confirmed"]
                context['request']['buttons'] = []
                context['request']['has_buttons'] = False
                # Don't forget to add task
                self.send(user, context)
                user["context"]["blogging"] = "fine"
                return base_state.OK
            else:
                user["context"]["blogging"] = "fine"
        if user["context"]["blogging"] == "fine":
            if context['request']['message']['text'] != self.strings["pass"]:
                user['answers']["story"] = context['request']['message']['text']
            context['request']['message']['text'] = self.strings["confirm_broadcast"]
            context['request']['buttons'] = []
            context['request']['has_buttons'] = False
            # Don't forget to add task
            self.send(user, context)
            del user["context"]["blogging"]
            text = self.strings["broadcast_message"].format(user["first_name"]) + user['answers']["story"]
            context["request"]["message"]["text"] = text
            await db.create_broadcast(context)
            return base_state.GO_TO_STATE(user["context"]["blogging_state"])
