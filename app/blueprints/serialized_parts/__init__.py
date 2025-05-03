from flask import Blueprint

serialized_part_bp = Blueprint('serialized_part_bp', __name__)
from . import routes  