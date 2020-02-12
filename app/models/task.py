import redis
import rq
from flask import current_app

from app import db_relational as db


class Task(db.Model):
    """Database model representing a Redis job task."""
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        """Retrieve Redis job object from the queue."""
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        """Retrieve progress of Redis job."""
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
