from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mongoengine import MongoEngine
from celery import Celery
import logging
from logging.handlers import RotatingFileHandler

import os
from datetime import datetime

from config import Config

db_relational = SQLAlchemy()
db_mongo = MongoEngine()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
bootstrap = Bootstrap()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)


def create_app(config_class=Config):
    """Creates the Flask app.

    :param config_class: Config class to use, default is the base config
        stored in the repository.
    """
    # Initiate Flask app and config
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure logging
    if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/' + datetime.now().strftime(
                'base-application_%H_%M_%S_%d_%m_%Y.log'),
            maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))

        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    app.logger.info('Base-application startup')

    # Initiate app components
    db_relational.init_app(app)
    migrate.init_app(app, db_relational)
    db_mongo.init_app(app)
    login.init_app(app)
    bootstrap.init_app(app)

    celery.conf.update(app.config)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.commands import ml
    app.register_blueprint(ml)

    return app
