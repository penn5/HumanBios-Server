from strings.qa_module import get_next_question
from db_models import ServiceTypes
from . import base_state


class QAState(base_state.BaseState):

    async def entry(self, context, user, db):
        question = get_next_question(user.identity, user.language)
        db[user.identity]['qa'] = {
            'q': question,
            'qa_results': {}
        }
        self.set_data(context, question)
        self.send(user, context)
        return base_state.OK

    async def process(self, context, user, db):
        curr_q = db[user.identity]['qa']['q']
        raw_answer = context['request']['message']['text']

        # Important: hack, has to be used to treat truncated answers from facebook
        if context['request']['service_in'] == ServiceTypes.FACEBOOK:
            for answer in curr_q.answers:
                if answer[:20] == raw_answer[:20]:
                    raw_answer = answer
                    break

        # `Not a legit answer` fallback
        if not curr_q.free and raw_answer not in curr_q.answers:
            context['request']['message']['text'] = self.strings['invalid_answer']
            context['request']['has_buttons'] = False
            self.send(user, context)
            return base_state.OK
        # Record the answer
        db[user.identity]['qa']['qa_results'][curr_q.id] = raw_answer
        # Find next question
        next_q_id = None

        # If question is free, just pick next one
        if curr_q.free:
            next_q_id = curr_q.answers
        # If answer in answers, map to the next question
        elif raw_answer in curr_q.answers:
            next_q_id = curr_q.answers[raw_answer]

        print(curr_q, f"\nnext id: {next_q_id}\n")
        # Get next question
        next_q = get_next_question(user.identity, user.language, next_q_id)
        # Set next question
        db[user.identity]['qa']['q'] = next_q
        if next_q:
            self.set_data(context, next_q)
        else:
            user.current_state = 10
            return base_state.GO_TO_STATE("BasicQuestionState")
        # Send message
        self.send(user, context)
        return base_state.OK

    def set_data(self, context, question):
        context['request']['message']['text'] = question.text
        if question.comment:
            context['request']['message']['text'] += f"\n\n{question.comment}"

        if not question.free:
            context['request']['has_buttons'] = True
            context['request']['buttons'] = [{"text": answer} for answer in question.answers]
            context['request']['buttons_type'] = "text"
        else:
            context['request']['has_buttons'] = False