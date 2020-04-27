import logging
from . import ROOT_PATH
import os

# Logging
logdir = os.path.join(ROOT_PATH, 'log')
logfile = os.path.join(logdir, 'server.log')
if not os.path.exists(logdir):
    os.mkdir(logdir)

logfile_handler = logging.handlers.WatchedFileHandler(logfile, 'a', 'utf-8')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("server").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.addHandler(logfile_handler)