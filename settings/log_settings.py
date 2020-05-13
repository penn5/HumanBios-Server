import logging
from . import ROOT_PATH
import os

# Logging
logdir = os.path.join(ROOT_PATH, 'log')
logfile = os.path.join(logdir, 'server.log')
debug_logfile = os.path.join(logdir, 'debug_server.log')
if not os.path.exists(logdir):
    os.mkdir(logdir)
formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%d-%b-%y %H:%M:%S'

logging.basicConfig(
    format=formatter,
    datefmt=date_format,
    level=logging.ERROR
)

logging.basicConfig(
    filename=logfile,
    filemode="a+",
    format=formatter,
    datefmt=date_format,
    level=logging.ERROR
)

logging.basicConfig(
    filename=debug_logfile,
    filemode="a+",
    format=formatter,
    datefmt=date_format,
    level=logging.DEBUG
)