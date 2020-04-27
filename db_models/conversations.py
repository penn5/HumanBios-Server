

class Conversation(object):
    def __init__(self, user1, user2):
        self.users = {
            user1.identity: user2,
            user2.identity: user1
        }
        # add properties such as date etc

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
