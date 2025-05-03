from flask import Flask
from app.models import db
from app.extensions import ma, limiter, cache
from app.blueprints.customers import customers_bp, routes
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.vehicles import vehicles_bp
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.part_description import part_description_bp
from app.blueprints.serialized_parts import serialized_part_bp


def create_app(config_class='DevelopmentConfig'):

    app = Flask(__name__)
    app.config.from_object(f'config.{config_class}')


    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    #register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(service_tickets_bp, url_prefix='/service-tickets')
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(part_description_bp, url_prefix='/part-description')
    app.register_blueprint(serialized_part_bp, url_prefix='/serialized-parts')
    
    return app