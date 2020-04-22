import hashlib


class UserIdentity:
    def __init__(self, user_id, service):
        self.user_id = int(user_id)
        self.service = service

    def hash(self):
        return str(hashlib.sha1(str(str(self.user_id) + self.service).encode()))