from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, delete
from . import part_description_bp
from .schemas import part_description_schema, part_descriptions_schema
from app.models import db, PartDescription
from app.extensions import limiter, cache
from app.utils.utils import encode_token, token_required


# part_description endpoints
# Add part_description
@part_description_bp.route("/", methods=["POST"])
@limiter.limit("3 per hour") # Added limiting because no need to add > 3 part_descriptions per hour
def add_part_description():
    try:
        part_description_data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # use data to create an instance of part_description
    new_part_description = PartDescription(**part_description_data)

    # add the new part_description to the session
    db.session.add(new_part_description)
    db.session.commit()

    return part_description_schema.jsonify(new_part_description), 201


# get all part_descriptions
@part_description_bp.route("/", methods=["GET"])
@cache.cached(timeout=60)  # aded caching because assessing part_descriptions is a common operation
def get_part_descriptions():  
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', default=10, type=int)


    if page:
        pagination = db.paginate(select(PartDescription), page=page, per_page=per_page)
        part_description = pagination.items

        if not part_description:
            return jsonify({"message": "No part_descriptions found"}), 404
        return part_descriptions_schema.jsonify(part_description)
    else:
        part_descriptions = db.session.execute(select(PartDescription)). scalars().all()

        if not part_desc:
            return jsonify({"message": "No mechanics found"}), 404
        
        return part_descriptions_schema.jsonify(part_descriptions), 200

# get part_description by id
@part_description_bp.route("/<int:part_description_id>", methods=["GET"])
def get_part_description(part_description_id):
    part_description = db.session.get(PartDescription, part_description_id)

    if part_description:
        return part_description_schema.jsonify(part_description), 200

    return jsonify({"error": "Invalid part description ID"}), 404


# update part_description
@part_description_bp.route("/<int:part_description_id>", methods=["PUT"])
@token_required
@limiter.limit("3 per hour") # Added additional limiting because no need to update > 3 part_descriptions per hour
def update_part_description(part_description_id):
    part_description = db.session.get(PartDescription, part_description_id)

    if not part_description:
        return jsonify({"error": "Invalid part description ID"}), 404
    
    try:
        part_description_data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in part_description_data.items():
        setattr(part_description, field, value)

    db.session.commit()
    return part_description_schema.jsonify(part_description), 200


# delete part_description
@part_description_bp.route("/<int:part_description_id>", methods=["DELETE"])
@token_required
def delete_part_description(part_description_id):
    part_description = db.session.get(PartDescription, part_description_id)

    if not part_description:
        return jsonify({"message": "Invalid part id"}), 404

    db.session.delete(part_description)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted part_description {part_description_id}"}), 200

@part_description_bp.route("/search", methods=['GET'])
def search_by_part_name():
    name = request.args.get('name')
    query = select(PartDescription).where(PartDescription.part_name.ilike(f"%{name}%"))
    results = db.session.execute(query).scalars().all()
    return part_descriptions_schema.jsonify(results)
                            




