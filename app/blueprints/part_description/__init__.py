from flask import Blueprint

bp = Blueprint('[name]', __name__) 
from . import routes  