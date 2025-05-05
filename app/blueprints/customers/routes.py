from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, delete
from . import customers_bp
from .schemas import customers_schema, customer_schema, login_schema
from app.models import db, Customer
from app.extensions import limiter, cache
from app.utils.utils import encode_token, token_required


# Customer endpoints
# login endpoint


@customers_bp.route("/login", methods=["POST"])
@limiter.limit("3 per hour")
def login():
    try:
        creds = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == creds['email'])
    customer = db.session.execute(query).scalars().first()
    
    if customer and customer.password == creds['password']:
        token = encode_token(customer.id)
        response = {
            'status': 'success',
            'message': 'Successfully Logged In.',
            'token': token
        }
        return jsonify({'token': token}), 200


# Add customer
@customers_bp.route("/", methods=["POST"])
@token_required
@limiter.limit("3 per hour") # Added limiting because no need to add > 3 customers per hour
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().first()
    
    new_customer = Customer(**customer_data)

    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201


# get all customers
@customers_bp.route("/", methods=["GET"])
@cache.cached(timeout=60)  # aded caching because assessing customers is a common operation
def get_customers():
    # pagination (page/per_page)
    
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    query =select (Customer)
    customers = db.paginate(query, page=page, per_page=per_page)
    return customers_schema.jsonify(customers)

# get customer by id
@customers_bp.route("/<int:id>", methods=["GET"])
def get_customer(id):
    query = select(Customer).where(Customer.id == id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({"message": "Invalid user ID"}), 404

    return customer_schema.jsonify(customer), 200


# update customer
@customers_bp.route("/", methods=["PUT"])
@token_required
@limiter.limit("3 per hour") # Added additional limiting because no need to update > 3 customers per hour
def update_customer(id):
    query = select(Customer).where(Customer.id == id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({"message": "Invalid user ID"}), 404
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for field, value in customer_data.items():  # unpacks customer_data dictionary
        setattr(
            customer, field, value
        )  # updates the values of the customer we queried out of the db

    db.session.commit()
    return customer_schema.jsonify(customer), 200


# delete customer
@customers_bp.route("/", methods=["DELETE"])
@token_required
def delete_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted customer {customer_id}"}), 200

# Query parameter to search customer by email
@customers_bp.route("/search", methods=["GET"])
def search_customers():
    email = request.args.get("email")
    
    query = select(Customer).where(Customer.email.like(f"%{email}%"))
    customer = db.session.execute(query).scalars().first()

    if not customer:
        return jsonify({"message": "No customer found"}), 404

    return customer_schema.jsonify(customer), 200


