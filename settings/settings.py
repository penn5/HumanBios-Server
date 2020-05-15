import logging
import dotenv
import os

dotenv.load_dotenv('.env')

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

SERVER_SECURITY_TOKEN = os.environ['SERVER_SECURITY_TOKEN']

CLOUD_TRANSLATION_API_KEY = os.environ['CLOUD_TRANSLATION_API_KEY']

DATABASE_URL = os.environ['DATABASE_URL']

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

N_CORES = int(os.environ['N_CORES'])
try:
    DEBUG = bool(eval(os.environ['DEBUG']))
except ValueError as e:
    DEBUG = None
    logging.error(f"Expected bool, got {os.environ['DEBUG']}")
