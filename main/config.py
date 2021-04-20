import os
from datetime import timedelta


class Development:
    DEBUG = True
    SECRET_KEY = "changeme"

    # Skipping the below configuration would trigger a 500
    # on bad api request with no auth headers case
    # Read more at flask jwt extended issue 86
    # https://github.com/vimalloc/flask-jwt-extended/issues/86
    PROPAGATE_EXCEPTIONS = True

    JWT_ACCESS_TOKEN_EXPIRES = False

    SQLALCHEMY_DATABASE_URI = "sqlite:///stego.db"

    # Suppress SQLALCHEMY_TRACK_MODIFICATIONS overhead warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TMP_UPLOAD_PATH = '/tmp'

    ENC_IMG_SAVE_PATH = 'images'
    APP_ROOT = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
    HOST_DOMAIN = 'http://localhost:8000'

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
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'postgresql://localhost/stegano'
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(7)

    ENC_IMG_SAVE_PATH = 'images'
    HOST_DOMAIN = 'https://stegano.sreenadh.me/'


class Testing(Development):
    DEBUG = True
    TESTING = True
    SECRET_KEY = "testsecret"
    JWT_ACCESS_TOKEN_EXPIRES = False

    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres'\
        '@localhost/stegano_test'

    # Suppress SQLALCHEMY_TRACK_MODIFICATIONS overhead warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ENC_IMG_SAVE_PATH = 'images'


configuration = {
    'dev': Development,
    'production': Production,
    'test': Testing
}