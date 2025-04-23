from flask import request, jsonify
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema
from marshmallow import ValidationError
from app.models import db, Service_Ticket, Mechanic
from sqlalchemy import select, delete


# Service Ticket endpoints
# Add service_ticket
@service_tickets_bp.route("/", methods=['POST'])
def add_ticket():
    try:
        # Deserialize and validate input data
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer = db.session.query(customer).filter_by(id=ticket_data['customer_id'])

    if customer:
        new_ticket = Service_Ticket(**ticket_data)   
    # use data to create an instance of service_ticket
    # new_ticket = Service_Ticket(
    #     date=ticket_data['date'], 
    #     type=ticket_data['type'], 
    #     status=ticket_data['status'],
    #     customer_id=ticket_data.get('customer_id'),
    #     vehicle_id=ticket_data.get('vehicle_id'),
    #     mechanic_id=ticket_data.get('mechanic_id')
    # )

    # add the new ticket to the session
    db.session.add(new_ticket)
    db.session.commit()
    
    return service_ticket_schema.jsonify(new_ticket), 201
    # return jsonify({'message': 'Customer not found'}), 404


# get all tickets
@service_tickets_bp.route('/', methods=['GET'])
def get_all_tickets():
    query = select(Service_Ticket)
    tickets = db.session.execute(query).scalars().all()
    
    if tickets:
        return service_tickets_schema.jsonify(tickets), 200 
    return jsonify({'message': 'No tickets found'}), 404


# get ticket by id
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['GET'])
def get_ticket(service_ticket_id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    ticket = db.session.get(Service_Ticket, service_ticket_id)

    if ticket is None:
        return jsonify({'message': "Invalid ticket ID"}), 404
    
    return service_ticket_schema.jsonify(ticket), 200

# # Add mechanic to ticket
# @service_tickets_bp.route('/<int:ticket_id>/add-mechanic/<int:mechanic_id>', methods=["PUT"])
# def add_mechanic(ticket_id, mechanic_id):
#     ticket = db.session.get(Service_Ticket, ticket_id)
#     mechanic = db.session.get(Mechanic, mechanic_id)

#     if ticket and mechanic:
#         if mechanic not in ticket.mechanics:
#             ticket.mechanics.append(mechanic)
#             db.session.commit()
#             return jsonify({
#                 "message": f"successfully added {mechanic.name} to the ticket",
#                 "ticket": service_ticket_schema.dump(ticket),
#                 "mechanics": mechanics_schema.dump(ticket.mechanics)
#             }), 200
        
#         return jsonify({"error": f"{mechanic.name} is already assigned to this ticket"})
#     return jsonify({
#         "message": "Invalid ticket or mechanic ID"
#     }), 404
    

# # remove mechanic from ticket
# @service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=["PUT"])
# def remove_mechanic(ticket_id, mechanic_id):
#     ticket = db.session.get(Service_Ticket, ticket_id)
#     mechanic = db.session.get(Mechanic, mechanic_id)

#     if ticket and mechanic:
#         if mechanic in ticket.mechanics:
#             ticket.mechanics.remove(mechanic)
#             db.session.commit()
#             return jsonify({
#                 "message": f"successfully remove {mechanic.name} from the ticket",
#                 "ticket": service_ticket_schema.dump(ticket),
#                 "mechanics": mechanics_schema.dump(ticket.mechanics)
#             }), 200
        
#         return jsonify({"error": f"{mechanic.name} was not assigned to this ticket"}), 400
#     return jsonify({
#         "message": "Invalid ticket or mechanic ID"
#     }), 400


# update ticket
@service_tickets_bp.route('/<int:id>', methods=['PUT'])
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
@service_tickets_bp.route('/<int:id>', methods=['DELETE'])
def delete_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    ticket = db.session.execute(query).scalars().first()
    
    if ticket is None:
        return jsonify({'message': "Invalid ticket ID"}), 404

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted ticket {id}"}), 200