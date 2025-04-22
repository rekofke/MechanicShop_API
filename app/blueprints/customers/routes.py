from flask import request, jsonify
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import customer_schema, customers_schema
from marshmallow import ValidationError
from app.models import db, Customer
from sqlalchemy import select, delete





# Customer endpoints
# Add customer
@customers_bp.route("/", methods=['POST'])
def add_customer():
    try:
        print("Request JSON:", request.json)
        # Deserialize and validate input data
        customer_data = customer_schema.load(request.json)
        print("Validated data:", customer_data)
    except ValidationError as e:
        print("Validation error:", e.messages)
        return jsonify(e.messages), 400
    
    # use data to create an instance of Customer
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])

    # add the new customer to the session
    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201



# get all customers
@customers_bp.route('/', methods=['GET'])
def get_customers():
    query = select(Customer)
    result = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(result), 200 

# get customer by id
@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    query = select(Customer).where(Customer.id == id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({'message': "Invalid user ID"}), 404
    
    return customer_schema.jsonify(customer), 200

# update customer
@customers_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    query = select(Customer).where(Customer.id == id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({'message': "Invalid user ID"}), 404
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in customer_data.items(): # unpacks customer_data dictionary
        setattr(customer, field, value) # updates the values of the customer we queried out of the db

    db.session.commit()
    return customer_schema.jsonify(customer), 200

# delete customer
@customers_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer(id):
    query = select(Customer).where(Customer.id == id)
    customer = db.session.execute(query).scalars().first()
    
    if customer is None:
        return jsonify({'message': "Invalid user ID"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted customer {id}"}), 200
