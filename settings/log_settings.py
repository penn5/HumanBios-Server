import logging
from . import ROOT_PATH
import os

# Logging
logdir = os.path.join(ROOT_PATH, 'log')
logfile = os.path.join(logdir, 'server.log')
if not os.path.exists(logdir):
    os.mkdir(logdir)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logfile_handler = logging.FileHandler(logfile, 'a', 'utf-8')
logfile_handler.setLevel(logging.INFO)
logfile_handler.setFormatter(formatter)
logger.addHandler(logfile_handler)