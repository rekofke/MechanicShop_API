from flask import blueprint

vehicles_bp = blueprint('vehicles_bp', __name__)

from . import routes