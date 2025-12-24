import os


class Configuration(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret_key')
    ALLOWED_USER_EMAIL = os.environ.get('ALLOWED_USER_EMAIL', 'user@example.com')
    DEV_USER_EMAIL = os.environ.get('DEV_USER_EMAIL', 'user@example.com')
