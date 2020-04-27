

class User(object):

    def __init__(self, user_id, service, identity, first_name=None, last_name=None, username=None):
        self.user_id = int(user_id)
        self.service = service
        # Completely unique identifier generated
        # from combination of user_id and service
        self.identity = identity
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

    def __eq__(self, other):
        if isinstance(other, User):
            return self.identity == other.identity
        if isinstance(other, str):
            return self.identity == other
        return False

    def __repr__(self):
        return f"User(id={self.user_id}, service={self.service})"
