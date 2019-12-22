from flask import render_template
from flask_login import login_required

from app.main import bp


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    """Example home page."""
    return render_template('index.html')
