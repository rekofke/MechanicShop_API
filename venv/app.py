from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Date, Table, Column, select
from typing import List, Optional

class Base(DeclarativeBase):
    pass

# create the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:C%40ntget1n@127.0.0.1/mechanic_db'
db = SQLAlchemy(model_class=Base)
ma = Marshmallow(app)

db.init_app(app)
migrate = Migrate(app, db)


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
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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
    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", secondary="vehicle_mechanic_association", overlaps="assigned_mechanics")

# Association table for many-to-many relationship between vehicles and mechanics
vehicle_mechanic_association = Table(
    'vehicle_mechanic_association',
    Base.metadata,
    Column('vehicle_id', Integer, ForeignKey('vehicles.id')),
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
        include_relationships = True  # Optional, includes relationships if needed

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class VehicleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle

vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service_Ticket

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

#* Endpoints

# Customer endpoints
# Add customer
@app.route("/customers", methods=['POST'])
def add_customer():
    try:
        print("Request JSON:", request.json)
        # Deserialize and validate input data
        customer_data = customer_schema.load(request.json)
        print("Validated data:", customer_data)
    except ValidationError as e:
        print("Validation error:", e.messages)
        return jsonify(e.messages), 400
    
    # use data to create an instance of Customer
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])

    # add the new customer to the session
    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201



# get all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    query = select(Customer)
    result = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(result), 200 

# get customer by id
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    query = select(Customer).where(Customer.id == id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({'message': "Invalid user ID"}), 404
    
    return customer_schema.jsonify(customer), 200

# update customer
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    query = select(Customer).where(Customer.id == id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({'message': "Invalid user ID"}), 404
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in customer_data.items(): # unpacks customer_data dictionary
        setattr(customer, field, value) # updates the values of the customer we queried out of the db

    db.session.commit()
    return customer_schema.jsonify(customer), 200

# delete customer
@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    query = select(Customer).where(Customer.id == id)
    customer = db.session.execute(query).scalars().first()
    
    if customer is None:
        return jsonify({'message': "Invalid user ID"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted customer {id}"}), 200

# Vehicle endpoints
# Add vehicle
@app.route("/vehicles", methods=['POST'])
def add_vehicle():
    try:
        # Deserialize and validate input data
        vehicle_data = vehicle_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # use data to create an instance of vehicle
    new_vehicle = Vehicle(
        make=vehicle_data['make'], 
        model=vehicle_data['model'], 
        customer_id=vehicle_data['customer_id']
    )

    # add the new vehicle to the session
    db.session.add(new_vehicle)
    db.session.commit()
    
    return vehicle_schema.jsonify(new_vehicle), 201

# get all vehicles
@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    query = select(Vehicle)
    result = db.session.execute(query).scalars().all()
    return vehicles_schema.jsonify(result), 200 

# get vehicle by id
@app.route('/vehicles/<int:id>', methods=['GET'])
def get_vehicle(id):
    query = select(Vehicle).where(Vehicle.id == id)
    vehicle = db.session.execute(query).scalars().first()

    if vehicle is None:
        return jsonify({'message': "Invalid vehicle ID"}), 404
    
    return vehicle_schema.jsonify(vehicle), 200

# update vehicle
@app.route('/vehicles/<int:id>', methods=['PUT'])
def update_vehicle(id):
    query = select(Vehicle).where(Vehicle.id == id)
    vehicle = db.session.execute(query).scalars().first()

    if vehicle is None:
        return jsonify({'message': "Invalid vehicle ID"}), 404
    try:
        vehicle_data = vehicle_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in vehicle_data.items():
        setattr(vehicle, field, value)

    db.session.commit()
    return vehicle_schema.jsonify(vehicle), 200

# delete vehicle
@app.route('/vehicles/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    query = select(Vehicle).where(Vehicle.id == id)
    vehicle = db.session.execute(query).scalars().first()
    
    if vehicle is None:
        return jsonify({'message': "Invalid vehicle ID"}), 404

    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted vehicle {id}"}), 200

# Mechanic endpoints
# Add mechanic
@app.route('/mechanics', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_mechanic = Mechanic(name=mechanic_data['name'], address=mechanic_data['address'])

    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201

# get all mechanics
@app.route('/mechanics', methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    result = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(result), 200

# get mechanic by id
@app.route('/mechanics/<int:id>', methods=['GET'])
def get_mechanic(id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic is None:
        return jsonify({"message": "Invalid mechanic ID"}), 404
    return mechanic_schema.jsonify(mechanic), 200

# update mechanic
@app.route('/mechanics/<int:id>', methods=['PUT'])
def update_mechanic(id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic is None:
        return jsonify({"message": "Invalid mechanic ID"}), 404
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in mechanic_data.items():
        setattr(mechanic, field, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200
    
# delete mechanic
@app.route('/mechanics/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic is None:
        return jsonify({"message": "Invalid mechanic ID"}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted mechanic {id}"}), 200

# Service Ticket endpoints
# Add service_ticket
@app.route("/tickets", methods=['POST'])
def add_ticket():
    try:
        # Deserialize and validate input data
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # use data to create an instance of service_ticket
    new_ticket = Service_Ticket(
        date=ticket_data['date'], 
        type=ticket_data['type'], 
        status=ticket_data['status'],
        customer_id=ticket_data.get('customer_id'),
        vehicle_id=ticket_data.get('vehicle_id'),
        mechanic_id=ticket_data.get('mechanic_id')
    )

    # add the new ticket to the session
    db.session.add(new_ticket)
    db.session.commit()
    
    return service_ticket_schema.jsonify(new_ticket), 201

# get all tickets
@app.route('/tickets', methods=['GET'])
def get_all_tickets():
    query = select(Service_Ticket)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200 

# get ticket by id
@app.route('/tickets/<int:id>', methods=['GET'])
def get_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    ticket = db.session.execute(query).scalars().first()

    if ticket is None:
        return jsonify({'message': "Invalid ticket ID"}), 404
    
    return service_ticket_schema.jsonify(ticket), 200

# update ticket
@app.route('/tickets/<int:id>', methods=['PUT'])
def update_service_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    ticket = db.session.execute(query).scalars().first()

    if ticket is None:
        return jsonify({'message': "Invalid ticket ID"}), 404
        
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in ticket_data.items():
        setattr(ticket, field, value)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200

# delete ticket
@app.route('/tickets/<int:id>', methods=['DELETE'])
def delete_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    ticket = db.session.execute(query).scalars().first()
    
    if ticket is None:
        return jsonify({'message': "Invalid ticket ID"}), 404

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted ticket {id}"}), 200

with app.app_context():
    db.create_all()
    # db.drop_all()

if __name__ == '__main__':
    app.run(debug=True)