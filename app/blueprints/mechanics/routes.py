from flask import request, jsonify
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from marshmallow import ValidationError
from app.models import db, Mechanic
from sqlalchemy import select, delete


# Mechanic endpoints
# Add mechanic
@mechanics_bp.route('/', methods=['POST'])
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
@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    result = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(result), 200

# get mechanic by id
@mechanics_bp.route('/<int:id>', methods=['GET'])
def get_mechanic(id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic is None:
        return jsonify({"message": "Invalid mechanic ID"}), 404
    return mechanic_schema.jsonify(mechanic), 200

# update mechanic
@mechanics_bp.route('/<int:id>', methods=['PUT'])
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
@mechanics_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic is None:
        return jsonify({"message": "Invalid mechanic ID"}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted mechanic {id}"}), 200
