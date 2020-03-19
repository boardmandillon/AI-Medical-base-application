import os
from dotenv import load_dotenv
from celery.schedules import crontab

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    ADMINS = []
    LANGUAGES = ['en']
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', True)

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'RELATIONAL_DB_URI',
        'postgresql://user:password@0.0.0.0:5432/vulturePostgres')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MONGODB_DB = os.environ.get('MONGODB_DATABASE', 'vultureMongo')
    MONGODB_HOST = os.environ.get('MONGODB_HOST', '0.0.0.0')
    MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
    MONGODB_CONNECT = False
    # MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME', 'user')
    # MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', 'password')

    REDIS_URL = os.environ.get('REDIS_URL', 'redis://')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://')
    CELERYBEAT_SCHEDULE = {
        'example_project_train': {
            'task': 'example_project_train',
            'schedule': crontab(minute=0, hour=0),
        }
    }