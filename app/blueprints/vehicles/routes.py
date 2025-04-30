from flask import request, jsonify
from app.blueprints.vehicles import vehicles_bp
from app.blueprints.vehicles.schemas import vehicle_schema, vehicles_schema
from marshmallow import ValidationError
from app.models import db, Vehicle
from sqlalchemy import select, delete
from app.extensions import limiter, cache
from app.utils.utils import encode_token, token_required


# Vehicle endpoints
# Add vehicle
@vehicles_bp.route("/", methods=['POST'])
# @token_required
# @limiter.limit("3 per hour")  # no need to add more than 3 vehicles per hour
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
# @cache.cached(timeout=60)  # added caching because assessing vehicles is a common operation
def get_vehicles():
    # pagination (page/per_page)
    try:
        page = int(request.args.get('page'))
        per_page = request.args.get('per_page')
        query = select(Vehicle)
        vehicles = db.paginate(query, page=page, per_page=per_page)
        return vehicles_schema.jsonify(vehicles), 200
    except:
        query = select(Vehicle)     
        vehicles = db.session.execute(query).scalars().all()
        return vehicles_schema.jsonify(vehicles), 200
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
@vehicles_bp.route('/', methods=['PUT'])
# @token_required
# @limiter.limit("3 per hour")  # Added additional limiting because no need to update > 3 vehicles per hour
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
@vehicles_bp.route('/', methods=['DELETE'])
# @token_required
def delete_vehicle(id):
    query = select(Vehicle).where(Vehicle.id == id)
    vehicle = db.session.execute(query).scalars().first()
    
    if vehicle is None:
        return jsonify({'message': "Invalid vehicle ID"}), 404

    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted vehicle {id}"}), 200


#lambda function to determine popularity by quantity of each vehicle make
@vehicles_bp.route("/popular", methods=["GET"])
def popular_vehicles():
    query = select(Vehicle)
    vehicles = db.session.execute(query).scalars().all()
    
    vehicles.sort(key=lambda vehicle : vehicle.make)
    
    for vehicle in vehicles:
        print(vehicle.make, vehicle.model.count)
    
    return vehicles_schema.jsonify(vehicles), 200

# query param to search for vehicles by make
@vehicles_bp.route("/search", methods=["GET"])
def search_vehicle():
    make = request.args.get("make")
    
    # query param to search for vehicle phrases LIKE
    query = select(Vehicle).where(Vehicle.make.like(make))