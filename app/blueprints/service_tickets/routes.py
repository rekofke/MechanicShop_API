from flask import request, jsonify
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.schemas import (
    service_ticket_schema,
    service_tickets_schema,
    edit_service_tickets_schema,
)
from app.blueprints.mechanics.schemas import (
    mechanics_schema,
    mechanic_schema,
    return_mechanic_schema,
    edit_mechanic_schema,
)
from marshmallow import ValidationError
from app.models import db, Service_Ticket, Mechanic
from sqlalchemy import select, delete
from app.models import Customer
from app.extensions import limiter, cache
from app.utils.utils import encode_token, token_required


# Service Ticket endpoints
# Add service_ticket
@service_tickets_bp.route("/", methods=["POST"])
# @token_required
# @limiter.limit("3 per hour") # no need to add more than 3 service tickets per hour
def add_ticket():
    try:
        # Deserialize and validate input data
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = db.session.get(Customer, ticket_data.get("customer_id"))

    if customer:
        new_ticket = Service_Ticket(**ticket_data)
    # use data to create an instance of service_ticket
    new_ticket = Service_Ticket(
        date=ticket_data["date"],
        type=ticket_data["type"],
        status=ticket_data["status"],
        customer_id=ticket_data.get("customer_id"),
        vehicle_id=ticket_data.get("vehicle_id"),
    )

    # add the new ticket to the session
    db.session.add(new_ticket)
    db.session.commit()

    return service_ticket_schema.jsonify(new_ticket), 201
    return jsonify({"message": "Customer not found"}), 404


# get all tickets
@service_tickets_bp.route("/", methods=["GET"])
@cache.cached(timeout=60)  # added caching because assessing tickets is a common operation
def get_all_tickets():
    query = select(Service_Ticket)
    tickets = db.session.execute(query).scalars().all()

    # # pagination (page/per_page)
    # try:
    #     page = int(request.args.get("page"))
    #     per_page = request.args.get("per_page")
    #     query = select(Customer)
    #     tickets = db.paginate(query, page=page, per_page=per_page)
    #     return service_tickets_schema.jsonify(tickets), 200
    # except:
    #     query = select(Service_Ticket)
    #     customers = db.session.execute(query).scalars().all()
    #     return service_tickets_schema.jsonify(customers), 200
    # query = select(Customer)
    # result = db.session.execute(query).scalars().all()
    # return customers_schema.jsonify(result), 200


# get ticket by id
@service_tickets_bp.route("/<int:service_ticket_id>", methods=["GET"])
def get_ticket(service_ticket_id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    ticket = db.session.get(Service_Ticket, service_ticket_id)

    if ticket is None:
        return jsonify({"message": "Invalid ticket ID"}), 404

    return service_ticket_schema.jsonify(ticket), 200


# # Add mechanic to ticket
@service_tickets_bp.route(
    "/<int:ticket_id>/add-mechanic/<int:mechanic_id>", methods=["PUT"]
)
@token_required
# @limiter.limit("3 per hour") # no need to add more than 3 mechanics to a ticket per hour
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
@service_tickets_bp.route(
    "/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"]
)
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Service_Ticket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if ticket and mechanic:
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)
            db.session.commit()
            return jsonify(
                {
                    "message": f"successfully remove {mechanic.name} from the ticket",
                    "ticket": service_ticket_schema.dump(ticket),
                    "mechanics": mechanics_schema.dump(ticket.mechanics),
                }
            ), 200

        return jsonify(
            {"error": f"{mechanic.name} was not assigned to this ticket"}
        ), 400
    return jsonify({"message": "Invalid ticket or mechanic ID"}), 400


# # update ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
@token_required
@limiter.limit(
    "3 per hour"
)  # Added additional limiting because no need to update > 3 tickets per hour
def edit_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    ticket = db.session.execute(query).scalars().first()

    if ticket is None:
        return jsonify({"message": "Invalid ticket ID"}), 404

    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for field, value in ticket_data.items():
        setattr(ticket, field, value)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


# delete ticket
@service_tickets_bp.route("/", methods=["DELETE"])
@token_required
def delete_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    ticket = db.session.execute(query).scalars().first()

    if ticket is None:
        return jsonify({"message": "Invalid ticket ID"}), 404

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted ticket {id}"}), 200


# Edit Tickets
# @service_tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
# def edit_ticket():
#     try:
#         mechanic_edits = edit_mechanic_schema(request.json)
#     except ValidationError as e:
#         return jsonify(e.messages), 400

#     query = select(Mechanic).where(Mechanic.id == id)
#     ticket = db.session.execute(query).scalars().first()

#     # ASK DYLAN IF THIS IS COORECT SETUP (NOT SURE HOW HIS LIBRARY TRANSLATES TO MY MECHANIC SHOP)
#     # set up for loop to edit tickets
#     for mechanic_id in mechanic_edits('add_mechanic_ids'):
#         query = select(Mechanic).where(Mechanic.id == mechanic_id)
#         mechanic = db.session.execute(query).scalars().first()

#         if mechanic and mechanic not in ticket:
#             ticket.mechanics.append(mechanic)

#     for mechanic_id in mechanic_edits('delete_mechanic_ids'):
#         query = select(Mechanic).where(Mechanic.id == mechanic_id)
#         mechanic = db.session.execute(query).scalars().first()

#         if mechanic and mechanic in ticket:
#             ticket.mechanics.remove(mechanic)

#     db.session.commit()
#     return return_mechanic_schema.jsonify(mechanic), 200

# lambda to get all tickets and sort by most popular services on tickets
# @service_tickets_bp.route("/popular", methods=["GET"])
# def popular_service():
#     query = select(Service_Ticket)
#     service_tickets = db.session.execute(query).scalars().all()

#     for ticket in service_tickets:
#         print(ticket.type, ticket.vehicle)

#     print(len(service_tickets))
