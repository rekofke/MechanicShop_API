from flask import request, jsonify
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import customer_schema, customers_schema
from marshmallow import ValidationError
from app.models import db, Customer
from sqlalchemy import select, delete
from app.extensions import limiter, cache
from app.utils.utils import encode_token, token_required


# Customer endpoints
# Add customer

@customers_bp.route("/login", methods=['POST'])
@limiter.limit("3 per hour")
def login():
    try:
        credentials = request.json
        username = credentials['email']
        password = credentials['password']
    except KeyError:
        return jsonify({'messages': "Invalid payload, expecting username and password"}), 400
    
    query = select(Customer).where(Customer.email == username) # LESSON 7 says (Customer.email == email) but throws error
    user = db.session.execute(query).scalar_one_or_none() # Query user table for a user with this email

    if user and user.password == password: # if we have a have a user associated with the username, validate the password
        auth_token  = encode_token(user.id, user.role.role_name)

        response = {
            "status": "success",
            "message": "Sucessfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "invalid email orpassword"}), 401
    
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
@cache.cached(timeout=60) # aded caching because assessing customers is a common operation
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
@customers_bp.route('/', methods=['PUT'])
@token_required
@limiter.limit("3 per hour") # Added additional limiting because no need to update > 3 customers per hour
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
@customers_bp.route('/', methods=['DELETE'])
@token_required
def delete_customer(customer_id): # recieves customer_id from the token
    query = select(Customer).where(Customer.id == id)
    customer = db.session.execute(query).scalars().first()
    
    if customer is None:
        return jsonify({'message': "Invalid user ID"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted customer {id}"}), 200
