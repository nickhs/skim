import os

DEBUG = os.getenv('DEBUG', True)
SECRET_KEY = os.getenv('SKIM_SECRET_KEY', 'secret')
SQLALCHEMY_DATABASE_URI = os.getenv('SKIM_DATABASE_URI', 'sqlite:////tmp/test.db')
