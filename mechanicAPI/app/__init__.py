from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from app.models import db
from app.extensions import ma, limiter, cache
from app.blueprints.customers import customers_bp, routes
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.vehicles import vehicles_bp
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.part_description import part_description_bp
from app.blueprints.serialized_parts import serialized_part_bp

SWAGGER_URL = '/api/docs' # Sets the endpoint for our documentation
API_URL = '/static/swagger.yaml' # Grabs host URL from swagger file

swagger_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Mechanic API",
        'doc_expansion': 'none',
        'persistAuthorization': 'True',
    }
)


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
    app.register_blueprint(part_description_bp, url_prefix='/part-descriptions')
    app.register_blueprint(serialized_part_bp, url_prefix='/serialized-parts')
    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL) # Registering our swagger blueprint
    
    return app