from flask import Flask
from app.models import db
from app.extensions import ma
from app.blueprints.customers import customers_bp, routes
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.vehicles import vehicles_bp
from app.blueprints.mechanics import mechanics_bp


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')


    db.init_app(app)
    ma.init_app(app)

    #register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(service_tickets_bp, url_prefix='/service_tickets')
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    
    return app