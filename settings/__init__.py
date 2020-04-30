from .settings import CLOUD_TRANSLATION_API_KEY
from .settings import FACEBOOK_BOT_1_TOKEN
from .settings import TELEGRAM_SECURITY_TOKEN
from .settings import SERVER_SECURITY_TOKEN
from .settings import TELEGRAM_INSTANCE_URL
from .settings import FACEBOOK_BOT_1_URL
from .settings import FACEBOOK_BOT_1_NAME
from .settings import ROOT_PATH
from .log_settings import logger
from collections import namedtuple
Config = namedtuple("Config", ['token', 'url'])

tokens = {
    #'telegram': Config(TELEGRAM_SECURITY_TOKEN, TELEGRAM_INSTANCE_URL),
    FACEBOOK_BOT_1_NAME: Config(FACEBOOK_BOT_1_TOKEN, FACEBOOK_BOT_1_URL),
    'server': SERVER_SECURITY_TOKEN,
    # Bot for tests, don't touch
    'tests_dummy_bot': Config('TEST_BOT_1111', 'http://dummy_url'),
}

__all__ = ['tokens', 'ROOT_PATH', 'logger', 'CLOUD_TRANSLATION_API_KEY']