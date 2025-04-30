from flask import request, jsonify
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import customer_schema, customers_schema, login_schema
from marshmallow import ValidationError
from app.models import db, Customer
from sqlalchemy import select, delete
from app.extensions import limiter, cache
from app.utils.utils import encode_token, token_required


# Customer endpoints
# login endpoint

@customers_bp.route("/login", methods=['POST'])
# @limiter.limit("3 per hour")
def login():
    try:
        credentials = login_schema.load(request.json) 
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify({'messages': "Invalid payload, expecting username and password"}), 400
    
    query = select(Customer).where(Customer.email == email) 
    customer = db.session.execute(query).scalars().first() # lesson 7 says scalar_one_or_none

    if customer and customer.password == password: # if we have a have a user associated with the username, validate the password
        token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Sucessfully Logged In.",
            "token": token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "invalid email or password"}), 401

# Add customer
@customers_bp.route('/', methods=['POST'])
# @limiter.limit("3 per hour") # Added limiting because no need to add > 3 customers per hour    
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
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'], password=customer_data['password'])

    # add the new customer to the session
    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201



# get all customers
@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=60) # aded caching because assessing customers is a common operation
def get_customers():
    
    # pagination (page/per_page)
    try:
        page = int(request.args.get('page'))
        per_page = request.args.get('per_page')
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(customers), 200
    except:
        query = select(Customer)     
        vehicles = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(customers), 200
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
# @token_required
# @limiter.limit("3 per hour") # Added additional limiting because no need to update > 3 customers per hour
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
# @token_required
def delete_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
    if not customer:
        return jsonify({'message': "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f"Successfully deleted customer {customer_id}"}), 200
