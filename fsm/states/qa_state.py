from strings.qa_module import get_next_question
from db_models import ServiceTypes
from . import base_state


class QAState(base_state.BaseState):

    async def entry(self, context, user, db):
        # Get the first question
        question = get_next_question(user.identity, user.language)
        # Create qa storage
        db[user.identity]['qa'] = {
            'q': question,
            'qa_results': {}
        }
        # Easy method to prepare context for question
        self.set_data(context, question)
        # Add sending task
        self.send(user, context)
        return base_state.OK

    async def process(self, context, user, db):
        # Get saved current question
        curr_q = db[user.identity]['qa']['q']
        # Alias for text answer
        raw_answer = context['request']['message']['text']

        # Handle edge buttons
        # If `stop` button -> kill dialog
        if raw_answer == self.strings['stop']:
            # Jump from current state to final `end` state
            return base_state.GO_TO_STATE("ENDState")

        # Important: hack, has to be used to treat truncated answers from facebook
        if context['request']['service_in'] == ServiceTypes.FACEBOOK:
            # For each answer, check if truncated answer is the beginning of real answer
            for answer in curr_q.answers:
                if answer[:20] == raw_answer[:20]:
                    # Set predicted answer value to the text alias
                    raw_answer = answer
                    break

        # @Important: `Not a legit answer` fallback
        # If question is not free AND answer is not in possible answers to the question
        if not curr_q.free and raw_answer not in curr_q.answers:
            # Send invalid answer text
            context['request']['message']['text'] = self.strings['invalid_answer']
            context['request']['has_buttons'] = False
            self.send(user, context)
            # Repeat the question
            self.set_data(context, curr_q)
            # Sent another message
            self.send(user, context)
            return base_state.OK
        # Record the answer
        db[user.identity]['qa']['qa_results'][curr_q.id] = raw_answer
        # Find next question
        next_q_id = None

        # If question is free, just get the next question
        if curr_q.free:
            # Set next id to the only possible question
            next_q_id = curr_q.answers
        # If answer in answers, map to the next question
        elif raw_answer in curr_q.answers:
            # In this questions, answers are the `answer`:`next_question` maps
            next_q_id = curr_q.answers[raw_answer]

        # Get next question via qa_module method
        next_q = get_next_question(user.identity, user.language, next_q_id)
        # Set next question
        db[user.identity]['qa']['q'] = next_q
        # If next question exists -> prepare data
        if next_q:
            self.set_data(context, next_q)
        # else, all qa path finished -> go back to the basic questions
        else:
            user.current_state = 10
            return base_state.GO_TO_STATE("BasicQuestionState")
        # Send message
        self.send(user, context)
        return base_state.OK

    # @Important: easy method to prepare context
    def set_data(self, context, question):
        # Set according text
        context['request']['message']['text'] = question.text
        # Sometimes questions have useful `note`
        if question.comment:
            context['request']['message']['text'] += f"\n\n{question.comment}"

        # Always have buttons
        context['request']['has_buttons'] = True
        context['request']['buttons_type'] = "text"
        # If not a free question -> add it's buttons
        if not question.free:
            context['request']['buttons'] = [{"text": answer} for answer in question.answers]
        else:
            context['request']['buttons'] = []
        # Always add edge buttons
        context['request']['buttons'] += [{"text": self.strings['stop']}]
