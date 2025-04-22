from flask import request, jsonify
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema
from marshmallow import ValidationError
from app.models import db, Service_Ticket
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
    
    # use data to create an instance of service_ticket
    new_ticket = Service_Ticket(
        date=ticket_data['date'], 
        type=ticket_data['type'], 
        status=ticket_data['status'],
        customer_id=ticket_data.get('customer_id'),
        vehicle_id=ticket_data.get('vehicle_id'),
        mechanic_id=ticket_data.get('mechanic_id')
    )

    # add the new ticket to the session
    db.session.add(new_ticket)
    db.session.commit()
    
    return service_ticket_schema.jsonify(new_ticket), 201

# get all tickets
@service_tickets_bp.route('/', methods=['GET'])
def get_all_tickets():
    query = select(Service_Ticket)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200 

# get ticket by id
@service_tickets_bp.route('/<int:id>', methods=['GET'])
def get_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    ticket = db.session.execute(query).scalars().first()

    if ticket is None:
        return jsonify({'message': "Invalid ticket ID"}), 404
    
    return service_ticket_schema.jsonify(ticket), 200

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