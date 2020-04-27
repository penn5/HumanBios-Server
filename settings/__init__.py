from .settings import FACEBOOK_SECURITY_TOKEN
from .settings import TELEGRAM_SECURITY_TOKEN
from .settings import SERVER_SECURITY_TOKEN
from .settings import TELEGRAM_INSTANCE_URL
from .settings import FACEBOOK_INSTANCE_URL
from .settings import ROOT_PATH
from .log_settings import logger

tokens = {
    'telegram': {TELEGRAM_SECURITY_TOKEN: TELEGRAM_INSTANCE_URL},
    'facebook': {FACEBOOK_SECURITY_TOKEN: FACEBOOK_INSTANCE_URL},
    'server': SERVER_SECURITY_TOKEN
}

__all__ = ['tokens', 'ROOT_PATH', 'logger']