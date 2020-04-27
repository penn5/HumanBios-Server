from .settings import FACEBOOK_SECURITY_TOKEN
from .settings import TELEGRAM_SECURITY_TOKEN
from .settings import SERVER_SECURITY_TOKEN
from .settings import ROOT_PATH

tokens = {
    'telegram': [TELEGRAM_SECURITY_TOKEN],
    'facebook': [FACEBOOK_SECURITY_TOKEN],
    'server': [SERVER_SECURITY_TOKEN]
}

__all__ = ['tokens', 'ROOT_PATH']