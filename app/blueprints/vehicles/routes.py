from flask import request, jsonify
from app.blueprints.vehicles import vehicles_bp
from app.blueprints.vehicles.schemas import vehicle_schema, vehicles_schema
from marshmallow import ValidationError
from app.models import db, Vehicle
from sqlalchemy import select, delete


# Vehicle endpoints
# Add vehicle
@vehicles_bp.route("/", methods=['POST'])
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
@vehicles_bp.route('/', methods=['GET'])
def get_vehicles():
    query = select(Vehicle)
    result = db.session.execute(query).scalars().all()
    return vehicles_schema.jsonify(result), 200 

# get vehicle by id
@vehicles_bp.route('/<int:id>', methods=['GET'])
def get_vehicle(id):
    query = select(Vehicle).where(Vehicle.id == id)
    vehicle = db.session.execute(query).scalars().first()

    if vehicle is None:
        return jsonify({'message': "Invalid vehicle ID"}), 404
    
    return vehicle_schema.jsonify(vehicle), 200

# update vehicle
@vehicles_bp.route('/<int:id>', methods=['PUT'])
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
@vehicles_bp.route('/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    query = select(Vehicle).where(Vehicle.id == id)
    vehicle = db.session.execute(query).scalars().first()
    
    if vehicle is None:
        return jsonify({'message': "Invalid vehicle ID"}), 404

    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted vehicle {id}"}), 200