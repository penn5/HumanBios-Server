from enum import IntEnum


class AccountType(IntEnum):
    COMMON = 1
    MEDIC = 2
    SOCIAL = 3


class User(object):
    types = AccountType

    def __init__(self,
                 user_id,
                 service,
                 identity,
                 via_instance,
                 first_name=None,
                 last_name=None,
                 username=None,
                 language='en',
                 current_state=None):
        self.user_id = user_id
        self.service = service
        # Completely unique identifier generated
        # from combination of user_id and service
        self.identity = identity
        self.via_instance = via_instance
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.account_type = None
        self.language = language
        self.profile_picture = None
        self.current_state = current_state

    def __eq__(self, other):
        if isinstance(other, User):
            return self.identity == other.identity
        if isinstance(other, str):
            return self.identity == other
        return False

    def __repr__(self):
        return f"User(id={self.user_id}, service={self.service})"
