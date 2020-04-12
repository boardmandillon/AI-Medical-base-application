from flask import Blueprint

ml_bp = Blueprint('ml', __name__)
cli_admin_bp = Blueprint('cli_admin', __name__)

from app.commands import commands
from app.commands import cli_admin
from app.projects.aap_diagnosis import commands
