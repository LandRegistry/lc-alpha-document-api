import os


class Config(object):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    IMAGE_DIRECTORY = '/home/vagrant/interim/'
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'docstore')
    DATABASE_USER = os.getenv('DATABASE_USER', 'lc-documents')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'lcalpha')
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME)
    LEGACY_ADAPTER_URI = "http://localhost:5007"
    ALLOW_DEV_ROUTES = True


class PreviewConfig(Config):
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'docstore')
    DATABASE_USER = os.getenv('DATABASE_USER', 'lc-documents')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'lcalpha')
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME)
    IMAGE_DIRECTORY = "~/interim/"
    LEGACY_ADAPTER_URI = "http://localhost:5007"
    ALLOW_DEV_ROUTES = True
