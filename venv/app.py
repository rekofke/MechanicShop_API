from flask import Flask
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Date, Table, Column
from typing import List, Optional

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:C%40ntget1n@localhost/mechanic_db'
db = SQLAlchemy()
ma = Marshmallow()

db.init_app(app)
ma.init_app(app)

class Customer(Base):
    __tablename__ = 'customers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(125))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    phone: Mapped[str] = mapped_column(String(50))
    
    # Relationships
    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="customer")
    tickets: Mapped[List["Service_Ticket"]] = relationship("Service_Ticket", back_populates="customer")

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # Changed to Integer for consistency
    make: Mapped[str] = mapped_column(String(150))
    model: Mapped[str] = mapped_column(String(150))
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'))
    
    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="vehicles")
    tickets: Mapped[List["Service_Ticket"]] = relationship("Service_Ticket", back_populates="vehicle")
    assigned_mechanics: Mapped[List["Mechanic"]] = relationship("Mechanic", secondary="vehicle_mechanic_association")

class Mechanic(Base):
    __tablename__ = 'mechanics'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    address: Mapped[str] = mapped_column(String(150))
    
    # Relationships
    tickets: Mapped[List["Service_Ticket"]] = relationship("Service_Ticket", back_populates="mechanic")
    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", secondary="vehicle_mechanic_association")

# Association table for many-to-many relationship between vehicles and mechanics
vehicle_mechanic_association = Table(
    'vehicle_mechanic_association',
    Base.metadata,
    Column('vehicle_id', String(150), ForeignKey('vehicles.id')),
    Column('mechanic_id', Integer, ForeignKey('mechanics.id'))
)

class Service_Ticket(Base):
    __tablename__ = 'tickets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[DateTime] = mapped_column(DateTime)
    type: Mapped[str] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(150))
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'))
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey('vehicles.id'))
    mechanic_id: Mapped[int] = mapped_column(Integer, ForeignKey('mechanics.id'))
    
    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="tickets")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="tickets")
    mechanic: Mapped["Mechanic"] = relationship("Mechanic", back_populates="tickets")


#* Schemas
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer

user_schema = CustomerSchema()
users_schema = CustomerSchema(many=True)

class VehicleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle

vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic

mechanic_schema = MechanicSchema()
mechaincs_schema = MechanicSchema()

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service_Ticket

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)