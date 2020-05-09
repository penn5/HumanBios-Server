from enum import IntEnum


class AccountType(IntEnum):
    COMMON = 1
    MEDIC = 2
    SOCIAL = 3


# @Important: Don't make it an enum - keep it `str` type
class ServiceTypes:
    TELEGRAM = "telegram"
    FACEBOOK = "facebook"
    WEBSITE = "website"