import dotenv
import os
dotenv.load_dotenv('.env')

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

SERVER_SECURITY_TOKEN = os.environ['SERVER_SECURITY_TOKEN']
TELEGRAM_SECURITY_TOKEN = os.environ['TELEGRAM_SECURITY_TOKEN']
FACEBOOK_SECURITY_TOKEN = os.environ['FACEBOOK_SECURITY_TOKEN']