
class OK:
    status = 1

    def __eq__(self, other):
        return self.status == other.status


class GO_TO_STATE:
    status = 2
    next_state = None

    def __init__(self, next_state):
        self.next_state = next_state

    def __eq__(self, other):
        return self.status == other.status


class BaseState(object):
    has_entry = True

    # Prepare state
    def __init__(self):
        pass

    async def entry(self, context, user):
        return OK
        #raise NotImplementedError("Please implement entry point for the state")

    async def process(self, context, user):
        return OK
        #raise NotImplementedError("Please implement event process method")