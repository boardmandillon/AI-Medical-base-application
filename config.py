import os
from dotenv import load_dotenv
from celery.schedules import crontab

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    LANGUAGES = ['en']
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', True)

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [MAIL_USERNAME]

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'RELATIONAL_DB_URI',
        'postgresql://vulture:vulturejP!^vx,E7z@0.0.0.0:5432/vulturePostgres')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MONGODB_DB = os.environ.get('MONGODB_DATABASE', 'vultureMongo')
    MONGODB_HOST = os.environ.get('MONGODB_HOST', '0.0.0.0')
    MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
    MONGODB_CONNECT = False
    MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME', 'vulture')
    MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', 'vultureUG6>3csK)6')

    REDIS_URL = os.environ.get('REDIS_URL', 'redis://')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://')
    CELERYBEAT_SCHEDULE = {
        'example_project_train': {
            'task': 'example_project_train',
            'schedule': crontab(minute=0, hour=0, day_of_week=0),
        },
        'aap_diagnosis_train': {
            'task': 'aap_diagnosis_train',
            'schedule': crontab(minute=0, hour=0, day_of_week=1),
        },
        'aap_diagnosis_test': {
            'task': 'aap_diagnosis_test',
            'schedule': crontab(minute=0, hour=0, day_of_week=1),
        },
        'aap_gyn_diagnosis_train': {
            'task': 'aap_gyn_diagnosis_train',
            'schedule': crontab(minute=0, hour=0, day_of_week=2),
        },
        'aap_men_diagnosis_train': {
            'task': 'aap_men_diagnosis_train',
            'schedule': crontab(minute=0, hour=0, day_of_week=3),
        },
        'aap_men_diagnosis_test': {
            'task': 'aap_men_diagnosis_test',
            'schedule': crontab(minute=0, hour=0, day_of_week=3),
        },
        'aap_women_diagnosis_train': {
            'task': 'aap_women_diagnosis_train',
            'schedule': crontab(minute=0, hour=0, day_of_week=4),
        },
        'aap_women_diagnosis_test': {
            'task': 'aap_women_diagnosis_test',
            'schedule': crontab(minute=0, hour=0, day_of_week=4),
        },
    }
