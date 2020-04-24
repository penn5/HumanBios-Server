import hashlib


class UserIdentity:
    def __init__(self, user_id, service_in):
        self.service_in = service_in
        self.user_id = int(user_id)

    def hash(self):
        return str(hashlib.sha1(str(str(self.user_id) + self.service_in).encode()))