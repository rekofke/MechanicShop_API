from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, delete
from . import service_tickets_bp
from .schemas import service_tickets_schema, service_ticket_schema, ReturnMechanicSchema
from app.blueprints.mechanics.schemas import mechanics_schema, mechanic_schema
from app.blueprints.serialized_parts.schemas import serialized_parts_schema, serialized_part_schema
from app.models import db, Service_Ticket, Mechanic, SerializedPart, PartDescription
from app.extensions import limiter, cache
from app.utils.utils import encode_token, token_required

# Service Ticket endpoints
# Add service_ticket
@service_tickets_bp.route("/", methods=["POST"])
# @token_required
@limiter.limit("3 per hour") # no need to add more than 3 service tickets per hour
def add_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # use data to create an instance of service_ticket
    new_service_ticket = Service_Ticket(**service_ticket_data)

    # add the new service_ticket to the session
    db.session.add(new_service_ticket)
    db.session.commit()

    return service_ticket_schema.jsonify(new_service_ticket), 201


# get all tickets
@service_tickets_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True) # added caching because assessing service_tickets is a common operation
def get_service_tickets():
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', default=10, type=int)


    if page:
        pagination = db.paginate(select(Service_Ticket), page=page, per_page=per_page)
        service_tickets = pagination.items

        if not service_tickets:
            return jsonify({"message": "No service_tickets found"}), 404
        return service_tickets_schema.jsonify(service_tickets)
    else:
        service_tickets = db.session.execute(select(Service_Ticket)). scalars().all()

        if not service_tickets:
            return jsonify({"message": "No service_tickets found"}), 404
        
        return service_tickets_schema.jsonify(service_tickets), 200


    
# get ticket by id
@service_tickets_bp.route("/<int:service_tickets_id>", methods=['GET'])
def get_service_ticket(service_tickets_id):
    service_tickets = db.session.get(Service_Ticket, service_tickets_id)

    if service_tickets:
        return service_tickets_schema.jsonify(service_tickets), 200
    
    return jsonify({"error": "invalid service_tickets ID"}), 400


# # Add mechanic to ticket
@service_tickets_bp.route("/<int:ticket_id>/add-mechanic/<int:mechanic_id>", methods=["PUT"])
# @token_required
@limiter.limit("3 per hour") # no need to add more than 3 mechanics to a ticket per hour
def add_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Service_Ticket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if ticket and mechanic:
        if mechanic not in ticket.mechanic:
            ticket.mechanic.append(mechanic)
            db.session.commit()
            return jsonify(
                {
                    "message": f"successfully added {mechanic.name} to the ticket",
                    "ticket": service_ticket_schema.dump(ticket),
                    "mechanics": mechanics_schema.dump(ticket.mechanic),
                }
            ), 200

        return jsonify({"error": f"{mechanic.name} is already assigned to this ticket"})
    return jsonify({"message": "Invalid ticket or mechanic ID"}), 404


# remove mechanic from ticket
@token_required
@service_tickets_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Service_Ticket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if ticket and mechanic:
        if mechanic in ticket.mechanic:
            ticket.mechanic.remove(mechanic)
            db.session.commit()
            return jsonify(
                {
                    "message": f"successfully remove {mechanic.name} from the ticket",
                    "ticket": service_ticket_schema.dump(ticket),
                    "mechanics": mechanics_schema.dump(ticket.mechanic),
                }
            ), 200

        return jsonify(
            {"error": f"{mechanic.name} was not assigned to this ticket"}
        ), 400
    return jsonify({"message": "Invalid ticket or mechanic ID"}), 400


# # update ticket
# @service_tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
# @token_required
# @limiter.limit("3 per hour")  # Added additional limiting because no need to update > 3 tickets per hour
# def edit_ticket(id):
#     query = select(Service_Ticket).where(Service_Ticket.id == id)
#     ticket = db.session.execute(query).scalars().first()

#     if ticket is None:
#         return jsonify({"message": "Invalid ticket ID"}), 404

#     try:
#         ticket_data = service_ticket_schema.load(request.json)
#     except ValidationError as e:
#         return jsonify(e.messages), 400

#     for field, value in ticket_data.items():
#         setattr(ticket, field, value)

#     db.session.commit()
#     return service_ticket_schema.jsonify(ticket), 200


# delete ticket
@service_tickets_bp.route("/", methods=["DELETE"])
# @token_required
def delete_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    ticket = db.session.execute(query).scalars().first()

    if ticket is None:
        return jsonify({"message": "Invalid ticket ID"}), 404

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted ticket {id}"}), 200


# Edit Tickets
@service_tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
def edit_ticket():
    try:
        mechanic_edits = edit_mechanic_schema(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.id == id)
    ticket = db.session.execute(query).scalars().first()

    # ASK DYLAN IF THIS IS COORECT SETUP (NOT SURE HOW HIS LIBRARY TRANSLATES TO MY MECHANIC SHOP)
    # set up for loop to edit tickets
    for mechanic_id in mechanic_edits('add_mechanic_ids'):
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in ticket:
            ticket.mechanics.append(mechanic)

    for mechanic_id in mechanic_edits('delete_mechanic_ids'):
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic in ticket:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

# lambda to get all tickets and sort by most popular services on tickets
@service_tickets_bp.route("/popular", methods=["GET"])
def popular_service():
    query = select(Service_Ticket)
    service_tickets = db.session.execute(query).scalars().all()

    for ticket in service_tickets:
        print(ticket.type, ticket.service_ticket)

    print(len(service_tickets))

# add serialized part to sercice ticket
@service_tickets_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=["PUT"])
@token_required
@limiter.limit("3 per hour") # no need to add more than 3 parts to a ticket per hour
def add_part(ticket_id, part_id):
    ticket = db.session.get(Service_Ticket, ticket_id)
    part = db.session.get(SerializedPart, part_id)
    
    if ticket and part and part:
        if not part.ticket_id:
            ticket.serialized_parts.append(part)
            db.session.commit()
            return jsonify(
                {
                    "message": f"successfully added {part.description.part_name} to the ticket",
                    "ticket": service_ticket_schema.dump(ticket),
                    "parts": serialized_parts_schema.dump(ticket.serialized_parts),
                }
            ), 200
        return jsonify({
            "error": "this part is already assigned to a ticket" 
                }), 400
    return jsonify({"error": "Invalid ticket or part ID"}), 400


# two routes to search for part not being used and apply to ticket
@service_tickets_bp.route("/<int:ticket_id>/add-to-cart/<int:description_id>", methods=["PUT"])
@token_required
@limiter.limit("3 per hour") # no need to add more than 3 parts to a ticket per hour
def add_to_cart(ticket_id, description_id):
    ticket = db.session.get(Service_Ticket, ticket_id)     
    description = db.session.get(PartDescription, description_id)
    
    #* Pythonic route
    parts = description.serialized_parts
    
    for part in parts:
        if not part.ticket_id:
            ticket.serialized_parts.append(part)
            db.session.commit()
            return jsonify(
                {
                    "message": f"successfully added {part.description.part_name} to the ticket",
                    "ticket": service_ticket_schema.dump(ticket),
                    "parts": serialized_parts_schema.dump(ticket.serialized_parts),
                }
            ), 200
    
    
    #* SQLAlcheymy route
    # query = select(SerializedPart).where(SerializedPart.desc_id == description_id, SerializedPart.ticket_id == None)
    # part = db.session.execute(query).scalars().first()
    
    # ticket.serialized_parts.append(part)
    # db.session.commit()
    # return jsonify(
    #     {
    #         "message": f"successfully added {part.description.part_name} to the ticket",
    #         "ticket": service_ticket_schema.dump(ticket),
    #         "parts": serialized_parts_schema.dump(ticket.serialized_parts),
    #     }
    # ), 200