from flask import Blueprint

bp = Blueprint('ml', __name__)

from app.commands import commands
from app.projects.aap_diagnosis import commands
