from flask import request, jsonify
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema, login_schema
from marshmallow import ValidationError
from app.models import db, Mechanic
from sqlalchemy import select, delete
from app.extensions import limiter, cache
from app.utils.utils import encode_token, token_required


# Mechanic endpoints
@mechanics_bp.route('/login', methods=['POST'])
def login():
    try:
        creds = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == creds['email'])
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic and mechanic.password == creds['password']:
        token = encode_token(mechanic.id)
        response = {
            'status': 'success',
            'message': 'Successfully Logged In.',
            'token': token
        }
        return jsonify({'token': token}), 200
        

# Add mechanic
@mechanics_bp.route('/', methods=['POST'])
# @token_required
@limiter.limit("3 per hour") # no need to add more than 3 mechanics per hour
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalars().first()
    
    new_mechanic = Mechanic(**mechanic_data)

    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201

# get all mechanics
@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True) # added caching because assessing mechanics is a common operation
def get_mechanics():
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', default=10, type=int)


    if page:
        pagination = db.paginate(select(Mechanic), page=page, per_page=per_page)
        mechanics = pagination.items

        if not mechanics:
            return jsonify({"message": "No mechanics found"}), 404
        return mechanics_schema.jsonify(mechanics)
    else:
        mechanics = db.session.execute(select(Mechanic)). scalars().all()

        if not mechanics:
            return jsonify({"message": "No mechanics found"}), 404
        
        return mechanics_schema.jsonify(mechanics), 200
# get mechanic by id
@mechanics_bp.route('/<int:id>', methods=['GET'])
def get_mechanic(id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic is None:
        return jsonify({"message": "Invalid mechanic ID"}), 404
    return mechanic_schema.jsonify(mechanic), 200

# update mechanic
@mechanics_bp.route('/', methods=['PUT'])
@token_required
@limiter.limit("3 per hour") # Added additional limiting because no need to update > 3 mechanics per hour
def update_mechanic():
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.get(Mechanic, request.mechanic_id)

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
@mechanics_bp.route('/', methods=['DELETE'])
@token_required
def delete_mechanic():
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.get(Mechanic, request.mechanic_id)
    
    if mechanic is None:
        return jsonify({"message": "Invalid mechanic ID"}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted mechanic."}), 200

#lambda function to which mechanics have worked on the most tickets
@mechanics_bp.route("/popularity/", methods=["GET"])
def popularity():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    
    mechanics.sort(key=lambda mechanic : len(mechanic.tickets), reverse=True)
    
    return mechanics_schema.jsonify(mechanics)
    # for mechanic in mechanics:
    #     print(mechanic.id, mechanic.ticket.count)
    
    # return mechanics_schema.jsonify(mechanics), 200
