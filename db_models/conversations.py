from . import User
import time


class Conversation(object):
    def __init__(self, user1, user2, type_):
        self.users = {
            user1.identity: user2,
            user2.identity: user1
        }
        self.type = type_
        # add properties such as date etc
        self.time = time.time()

    def get_type(self, user_identity):
        return self.users[user_identity].account_type

    def get_user(self, user_identity):
        return self.users[user_identity]

    def __eq__(self, other):
        if isinstance(other, Conversation):
            return self.users == other.users
        if isinstance(other, str):
            return other in self.users
        return False

    def __repr__(self):
        users = list(self.users.values())
        return f"Conversation(user1={users[0]}, user2={users[1]})"


class ConversationRequest(object):
    def __init__(self, user_identity, type_: User.types):
        self.user_identity = user_identity
        self.type = type_
        self.waiting_since = int(time.time())

    def __eq__(self, other):
        if isinstance(other, ConversationRequest):
            return self.user_identity == other.user_identity
        if isinstance(other, str):
            return self.user_identity == other
        return False

    def __repr__(self):
        return "ConversationRequest: (user_identity: {}, type: {}, waiting_since: {})".format(self.user_identity,
                                                                                              self.type,
                                                                                              self.waiting_since)


class ConversationRequests:
    _requests = list()

    def __init__(self):
        pass

    def add(self, req: ConversationRequest):
        if req in self._requests:
            raise Exception("User already waiting")
        self._requests.append(req)

    def get_request_by_user(self, user_entity):
        for req in self._requests:
            if req.user_entity == user_entity:
                return req
        return None

    def has_user_request(self, user_entity):
        return self.get_request_by_user(user_entity) is not None

    def close(self, req):
        try:
            self._requests.remove(req)
        except ValueError:
            pass

    def close_by_user(self, user_entity):
        try:
            req = self.get_request_by_user(user_entity)
            if req is not None:
                self._requests.remove(req)
        except ValueError:
            pass

    def get_waiting_requests(self, waiting_minutes=15):
        now = int(time.time())
        tmp_reqs = list()
        for req in self._requests:
            time_diff = now - req.waiting_since
            if time_diff >= waiting_minutes * 60:
                tmp_reqs.append(req)

        return tmp_reqs


class ConversationDispatcher(object):
    __instance = None
    LIMIT_CONCURRENT_CHATS = 100

    def __init__(self):
        if ConversationDispatcher._initialized:
            return
        self.conversation_requests = ConversationRequests()
        self.active_conversations = []
        ConversationDispatcher._initialized = True

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(ConversationDispatcher, cls).__new__(cls)
        return cls.__instance

    def limit_reached(self):
        """Returns True if the number of current active conversations exceed the defined limit"""
        return len(self.active_conversations) >= self.LIMIT_CONCURRENT_CHATS

    def is_user_waiting(self, user_entity):
        return self.conversation_requests.has_user_request(user_entity)

    def get_waiting_requests(self, waiting_minutes=15):
        """Returns a list of requests waiting for over 15 minutes"""
        return self.conversation_requests.get_waiting_requests(waiting_minutes)

    def has_active_conversation(self, user_entity):
        """Checks if a user has active conversations"""
        return self.get_conversation(user_entity) is not None

    def get_conversation(self, user_entity):
        """Returns the Conversation object for a certain user"""
        for conv in self.active_conversations:
            if conv.worker == user_entity or conv.user == user_entity:
                return conv

        return None

    def new_conversation(self, user_entity, worker_entity):
        req = self.conversation_requests.get_request_by_user(user_entity)

        conv = Conversation(worker_entity, user_entity, req.type)
        self.active_conversations.append(conv)

        self.conversation_requests.close(req)

    def stop_conversation(self, user_entity):
        conv = self.get_conversation(user_entity)
        if conv is not None:
            self.active_conversations.remove(conv)

    def request_conversation(self, user: User, type_: User.types):
        req = ConversationRequest(user.identity, type_)
        self.conversation_requests.add(req)