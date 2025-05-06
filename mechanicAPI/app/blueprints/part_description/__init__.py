from flask import Blueprint

part_description_bp = Blueprint('part_description_bp', __name__)
from . import routes  