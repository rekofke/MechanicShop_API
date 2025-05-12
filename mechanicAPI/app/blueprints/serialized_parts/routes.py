from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, delete
from . import serialized_part_bp
from .schemas import serialized_part_schema, serialized_parts_schema
from app.models import SerializedPart
from app.models import PartDescription
from app.extensions import limiter, cache, db
from app.utils.utils import encode_token, token_required


#* serialized_part endpoints
#* Add serialized_part
@serialized_part_bp.route("/", methods=["POST"])
@limiter.limit("3 per hour") # Added limiting because no need to add > 3 serialized_parts per hour
def add_serialized_part():
    try:
        serialized_part_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # use data to create an instance of serialized_part
    new_serialized_part = SerializedPart(**serialized_part_data)

    # add the new serialized_part to the session
    db.session.add(new_serialized_part)
    db.session.commit()

    return jsonify({
            "message": f"Added new {new_serialized_part.description.brand} {new_serialized_part.description.part_name} to serialized_parts",
            "part": serialized_part_schema.dump(new_serialized_part)
    })
            


#* get all serialized_parts
@serialized_part_bp.route("/", methods=["GET"])
@cache.cached(timeout=60)  # aded caching because assessing serialized_parts is a common operation
def get_serialized_parts():
    # Differnt way to paginate...
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', default=10, type=int)


    if page:
        pagination = db.paginate(select(SerializedPart), page=page, per_page=per_page)
        serialized_part = pagination.items

        if not serialized_part:
            return jsonify({"message": "No serialized_parts found"}), 404
        return serialized_parts_schema.jsonify(serialized_part)
    else:
        serialized_parts = db.session.execute(select(SerializedPart)). scalars().all()

        if not serialized_parts:
            return jsonify({"message": "No mechanics found"}), 404
        
        return serialized_parts_schema.jsonify(serialized_parts), 200

# get serialized_part by id
@serialized_part_bp.route("/<int:serialized_part_id>", methods=["GET"])
def get_serialized_part(serialized_part_id):
    serialized_part = db.session.get(SerializedPart, serialized_part_id)

    if serialized_part:
        return serialized_part_schema.jsonify(serialized_part), 200

    return jsonify({"error": "Invalid part description ID"}), 404


#* update serialized_part
@serialized_part_bp.route("/<int:serialized_part_id>", methods=["PUT"])
@token_required
@limiter.limit("3 per hour") # Added additional limiting because no need to update > 3 serialized_parts per hour
def update_serialized_part(serialized_part_id):
    serialized_part = db.session.get(SerializedPart, serialized_part_id)

    if not serialized_part:
        return jsonify({"error": "Invalid part description ID"}), 404
    
    try:
        serialized_part_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in serialized_part_data.items():
        setattr(serialized_part, field, value)

    db.session.commit()
    return serialized_part_schema.jsonify(serialized_part), 200


#* delete serialized_part
@serialized_part_bp.route("/<int:serialized_part_id>", methods=["DELETE"])
@token_required
def delete_serialized_part(serialized_part_id):
    serialized_part = db.session.get(SerializedPart, serialized_part_id)

    if not serialized_part:
        return jsonify({"message": "Invalid part id"}), 404

    db.session.delete(serialized_part)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted serialized_part {serialized_part_id}"}), 200

# search for like terms
@serialized_part_bp.route("/search", methods=['GET'])
def search_by_part_name():
    name = request.args.get('name')
    query = select(serialized_part).where(serialized_part.name.like(f"%{name}%"))
    serialized_part = db.session.execute(query.scalars().first())
    
    return serialized_part_schema.jsonify(serialized_part), 200
                            

#* search for total inventory by part description
@serialized_part_bp.route("/stock/<int:description_id>", methods=["GET"])
def get_individual_stock(description_id):
    serialized_part = db.session.get(PartDescription, description_id)
    
    # get list of serialized parts
    parts = serialized_part.serialized_parts
    
    count = 0
    for part in parts:
        if not part.ticket_id:
            count += 1
            
    return jsonify({
        "item": serialized_part.part_name,
        "quantity": count
    })


