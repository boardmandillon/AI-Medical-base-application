from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import users, errors, tokens
from app.api.projects import aap_diagnosis, aap_gyn_diagnosis, \
    urine_dipstick_analysis, pointofcareOCR, example_project
