from server_logic.definitions import Context
from strings.qa_module import get_next_question, get_user_scores
from db_models import ServiceTypes, User
from . import base_state


class QAState(base_state.BaseState):

    async def entry(self, context: Context, user: User, db):
        # Get the first question
        question = get_next_question(user['identity'], user['language'])
        # Create qa storage
        user['answers']['qa'] = {
            'q': question.id,
            'qa_results': {},
            'score': 0
        }
        # Easy method to prepare context for question
        self.set_data(context, question)
        # Add sending task
        self.send(user, context)
        return base_state.OK

    async def process(self, context: Context, user: User, db):
        # Get saved current question
        curr_q = get_next_question(user['identity'], user['language'], user['answers']['qa']['q'])
        # Alias for text answer
        raw_answer = context['request']['message']['text']
        # Save current score
        user['answers']['qa']['score'] = get_user_scores(user['identity'])
        # print(user['answers']['qa']['score'])
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
        user['answers']['qa']['qa_results'][curr_q.id] = raw_answer
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
        next_q = get_next_question(user['identity'], user['language'], next_q_id)
        # If next question is a string, its the final recommendation. we will send it out then switch
        if isinstance(next_q, str):
            context['request']['message']['text'] = next_q
            context['request']['has_buttons'] = False
            self.send(user, context)
            user['context']['bq_state'] = 10
            return base_state.GO_TO_STATE("BasicQuestionState")
        # If next question exists -> prepare data
        else:
            # Set next question
            user['answers']['qa']['q'] = next_q.id
            self.set_data(context, next_q)
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
