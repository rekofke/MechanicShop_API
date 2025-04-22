from flask import Flask
from app.models import db
from app.extensions import ma
from app.blueprints.customers import customers_bp


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')


    db.init_app(app)
    ma.init_app(app)

    #register blueprints
    app.register_blueprints(customers_bp, url_prefix='/customers')
    
    return app