import os

DEBUG = os.getenv('DEBUG', True)
SECRET_KEY = os.getenv('SKIM_SECRET_KEY', 'secret')
SQLALCHEMY_DATABASE_URI = os.getenv('SKIM_DATABASE_URI', 'sqlite:////tmp/test.db')
DIFFBOT_ENDPOINT = os.getenv('SKIM_DIFFBOT_URL', 'http://www.diffbot.com/api/article')
DIFFBOT_TOKEN = os.getenv('SKIM_DIFFBOT_TOKEN', 'e2bf1a515d3430ee68bbfb16003dadf2')
