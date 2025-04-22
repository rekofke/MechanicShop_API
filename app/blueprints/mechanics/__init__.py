from flask import blueprint

mechanics_bp = blueprint('mechanics_bp', __name__)

from . import routes