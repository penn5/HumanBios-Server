from .settings import CLOUD_TRANSLATION_API_KEY
from .settings import SERVER_SECURITY_TOKEN
from .settings import ROOT_PATH
from .settings import N_CORES
from .settings import DEBUG
from collections import namedtuple
import logging
import os
Config = namedtuple("Config", ['token', 'url'])

tokens = {
    'server': SERVER_SECURITY_TOKEN,
    # Bot for tests, don't touch
    'tests_dummy_bot': Config('TEST_BOT_1111', 'http://dummy_url'),
}

__all__ = ['tokens', 'ROOT_PATH', 'CLOUD_TRANSLATION_API_KEY', 'Config', 'N_CORES', 'DEBUG']


# Logging
logdir = os.path.join(ROOT_PATH, 'log')
logfile = os.path.join(logdir, 'server.log')
if not os.path.exists(logdir):
    os.mkdir(logdir)
formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%d-%b-%y %H:%M:%S'

logging.basicConfig(
    format=formatter,
    datefmt=date_format,
    level=logging.INFO
)

logging.basicConfig(
    filename=logfile,
    filemode="a+",
    format=formatter,
    datefmt=date_format,
    level=logging.ERROR
)

