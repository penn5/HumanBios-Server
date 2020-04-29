import dotenv
import os
dotenv.load_dotenv('.env')

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

SERVER_SECURITY_TOKEN = os.environ['SERVER_SECURITY_TOKEN']
TELEGRAM_SECURITY_TOKEN = os.environ['TELEGRAM_SECURITY_TOKEN']
TELEGRAM_INSTANCE_URL = os.environ['TELEGRAM_INSTANCE_URL']

FACEBOOK_BOT_1_NAME = os.environ['FACEBOOK_BOT_1_NAME']
FACEBOOK_BOT_1_URL = os.environ['FACEBOOK_BOT_1_URL']
FACEBOOK_BOT_1_TOKEN = os.environ['FACEBOOK_BOT_1_TOKEN']
