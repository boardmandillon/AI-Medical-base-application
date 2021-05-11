from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import users , errors , tokens
from app.api.projects import aap_diagnosis , aap_gyn_diagnosis , \
    urine_dipstick_analysis , example_project , \
    skin_cancer_analysis , point_of_care_ocr_analysis
