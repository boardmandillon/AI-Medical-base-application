import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    ADMINS = []
    LANGUAGES = ['en']
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'RELATIONAL_DB_URI',
        'postgresql://user:password@localhost:5432/vulturePostgres')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MONGODB_DB = os.environ.get('MONGODB_DATABASE', 'vultureMongo')
    MONGODB_HOST = os.environ.get('MONGODB_HOST', 'localhost')
    MONGODB_PORT = os.environ.get('MONGODB_PORT', 27017)
    # MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME', 'user')
    # MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', 'password')
