from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, ForeignKey, Table, Column
from typing import List
from app.extensions import db


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Association table for many-to-many relationship between vehicles and mechanics
vehicle_mechanic_association = db.Table(
    'vehicle_mechanic_association',
    Base.metadata,
    Column('vehicle_id', Integer, ForeignKey('vehicles.id')),
    Column('mechanic_id', Integer, ForeignKey('mechanics.id'))
)
service_mechanic = db.Table(
    'service_mechanic',
    Base.metadata,
    Column('service_id', Integer, ForeignKey('tickets.id')),
    Column('mechanic_id', Integer, ForeignKey('mechanics.id'))
)

class Customer(Base):
    __tablename__ = 'customers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(125), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    phone: Mapped[str] = mapped_column(String(50))
    
    
    # Relationships
    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="customer")
    tickets: Mapped[List["Service_Ticket"]] = relationship("Service_Ticket", back_populates="customer")

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    make: Mapped[str] = mapped_column(String(150))
    model: Mapped[str] = mapped_column(String(150))
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'))
    
    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="vehicles")
    tickets: Mapped[List["Service_Ticket"]] = relationship("Service_Ticket", back_populates="vehicle")
    assigned_mechanics: Mapped[List["Mechanic"]] = relationship("Mechanic", secondary=vehicle_mechanic_association)

class Mechanic(Base):
    __tablename__ = 'mechanics'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    address: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Relationships
    tickets: Mapped[List["Service_Ticket"]] = relationship(secondary=service_mechanic, back_populates="mechanic")
    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", secondary=vehicle_mechanic_association, overlaps="assigned_mechanics")




class Service_Ticket(Base):
    __tablename__ = 'tickets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[DateTime] = mapped_column(DateTime)
    type: Mapped[str] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(150))
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'))
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey('vehicles.id'))

    # Relationships
    customer: Mapped["Customer"] = db.relationship(back_populates="tickets")
    vehicle: Mapped["Vehicle"] = db.relationship("Vehicle", back_populates="tickets")
    mechanic: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanic, back_populates="tickets")
    serialized_parts: Mapped[List['SerializedPart']] = db.relationship("SerializedPart", back_populates="ticket")
    
class PartDescription(Base):
    __tablename__ = 'part_descriptions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    part_name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    
    serialized_parts: Mapped[List['SerializedPart']] = db.relationship("SerializedPart", back_populates="description")
    
class SerializedPart(Base):
    __tablename__ = 'serialized_parts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    desc_id: Mapped[int] = mapped_column(ForeignKey('part_descriptions.id'), nullable=False)
    ticket_id: Mapped[int] = mapped_column(ForeignKey('tickets.id'), nullable=True)
    
    description: Mapped["PartDescription"] = db.relationship("PartDescription", back_populates="serialized_parts")
    ticket: Mapped["Service_Ticket"] = db.relationship(back_populates="serialized_parts")