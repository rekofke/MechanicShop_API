from flask import request, jsonify
from app.blueprints.part_description import part_description
from app.blueprints.part_description.schemas import (partdescription_schema as part_description_schema, partdescriptions_schema as part_descriptions_schema)
from marshmallow import ValidationError
from app.models import db, PartDescription
from sqlalchemy import select, delete
from app.extensions import limiter, cache
from app.utils.utils import encode_token, token_required


# part_description endpoints
# Add part_description
@part_description.bp.route("/", methods=["POST"])
# @limiter.limit("3 per hour") # Added limiting because no need to add > 3 part_descriptions per hour
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
@part_description.bp.route("/", methods=["GET"])
@cache.cached(timeout=60)  # aded caching because assessing part_descriptions is a common operation
def get_part_descriptions():
    # Differnt way to paginate...
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    query =select (PartDescription)
    part_descriptions = db.paginate(query, page=page, per_page=per_page)
    return part_descriptions_schema.jsonify(part_descriptions)

# get part_description by id
@part_description.bp.route("/<int:part_description_id>", methods=["GET"])
def get_part_description(part_description_id):
    part_description = db.session.get(PartDescription, part_description_id)

    if part_description:
        return part_description_schema.jsonify(part_description), 200

    return jsonify({"error": "Invalid part description ID"}), 404


# update part_description
@part_description.bp.route("/<int:part_description_id>", methods=["PUT"])
@token_required
# @limiter.limit("3 per hour") # Added additional limiting because no need to update > 3 part_descriptions per hour
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
@part_description.bp.route("/<int:part_description_id", methods=["DELETE"])
@token_required
def delete_part_description(part_description_id):
    part_description = db.session.get(PartDescription, part_description_id)

    if not part_description:
        return jsonify({"message": "Invalid part id"}), 404

    db.session.delete(part_description)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted part_description {part_description_id}"}), 200




