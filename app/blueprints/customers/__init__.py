from flask import blueprint

customers_bp = blueprint('customers_bp', __name__)

from . import routes