import os


class Development:
    DEBUG = True
    SECRET_KEY = "changeme"
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = MAIL_USERNAME


class Production(Development):
    DEBUG = False
    SECRET_KEY = ""


class Testing(Development):
    DEBUG = True
    TESTING = True
    SECRET_KEY = "testsecret"


configuration = {
    'dev': Development,
    'production': Production,
    'test': Testing
}
