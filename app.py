from app import create_app
from app.models import db

# from flask import Flask, request, jsonify
# from flask_migrate import Migrate
# from flask_marshmallow import Marshmallow
# from marshmallow import ValidationError
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
# from sqlalchemy import Integer, String, DateTime, ForeignKey, Date, Table, Column, select
# from typing import List, Optional


app = create_app('DevelopmentConfig')


with app.app_context():
    db.create_all()
    # db.drop_all()



    app.run()