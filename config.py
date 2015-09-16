import os


class Config(object):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_NAME = 'docstore'
    DATABASE_USER = 'landcharges'
    DATABASE_PASSWORD = 'lcalpha'
    DATABASE_HOST = 'localhost'
    IMAGE_DIRECTORY = '/home/vagrant/'


class PreviewConfig(Config):
    DATABASE_NAME = 'docstore'
    DATABASE_USER = 'landcharges'
    DATABASE_PASSWORD = 'lcalpha'
    DATABASE_HOST = 'localhost'
