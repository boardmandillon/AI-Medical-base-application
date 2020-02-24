from flask_mongoengine import MongoEngine

from app import celery, create_app

app = create_app()
app.app_context().push()

db_mongo = MongoEngine()
db_mongo.init_app(app)
