

class AccountType:
    COMMON = 1
    MEDIC = 2
    SOCIAL = 3


# @Important: Don't make it an enum (type from `typing` module) - keep it `str` type for the sake of db
class ServiceTypes:
    TELEGRAM = "telegram"
    FACEBOOK = "facebook"
    WEBSITE = "website"