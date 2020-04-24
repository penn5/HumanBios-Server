import dotenv
import os
dotenv.load_dotenv('.env')

# Botsociety config
B_VERSION = os.environ['BOTSOCIETY_API_VERSION']
B_URL = os.environ['BOTSOCIETY_API_URL']
B_KEY = os.environ['BOTSOCIETY_API_KEY']
B_ID = os.environ['BOTSOCIETY_USER_ID']