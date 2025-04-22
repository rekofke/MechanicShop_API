from flask import blueprint

service_tickets_bp = blueprint('service_tickets_bp', __name__)

from . import routes