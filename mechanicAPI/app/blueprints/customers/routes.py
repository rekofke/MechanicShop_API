from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, delete
from . import customers_bp
from .schemas import customer_schema, customers_schema
from app.models import db, Customer
from app.extensions import limiter, cache
from app.utils.utils import encode_token, token_required


# customer endpoints
# Add customer
@customers_bp.route("/", methods=["POST"])
@limiter.limit("3 per hour") # Added limiting because no need to add > 3 customers per hour
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    # use data to create an instance of customer
    new_customer = Customer(**customer_data)

    # add the new customer to the session
    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201


# get all customers
@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True) # added caching because assessing customers is a common operation
def get_customers():
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', default=10, type=int)


    if page:
        pagination = db.paginate(select(Customer), page=page, per_page=per_page)
        customers = pagination.items

        if not customers:
            return jsonify({"message": "No customers found"}), 404
        return customers_schema.jsonify(customers)
    else:
        customers = db.session.execute(select(Customer)). scalars().all()

        if not customers:
            return jsonify({"message": "No customers found"}), 404
        
        return customers_schema.jsonify(customers), 200

# get single customer
@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    
    return jsonify({"error": "invalid customer ID"}), 400

# update customer
@customers_bp.route("/<int:customer_id>", methods=["PUT"])
@token_required
@limiter.limit("3 per hour") # Added additional limiting because no need to update > 3 customers per hour
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Invalid part description ID"}), 404
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in customer_data.items():
        setattr(customer, field, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


# delete customer
@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
@token_required
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"message": "Invalid part id"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted customer {customer_id}"}), 200

#* Query Parameters
# Search for customer by name
@customers_bp.route("/search", methods=['GET'])
def search_by_name():
    name = request.args.get('name')
    print(name)
    query = select(Customer).where(Customer.name.like(f"%{name}%"))
    customer = db.session.execute(query).scalars().first()
    print(customer)
    return customer_schema.jsonify(customer), 200

# Search for customer by email
@customers_bp.route("/search", methods=['GET'])
def search_by_email():
    email = request.args.get('email')
    print(email)
    query = select(Customer).where(Customer.email.like(f"%{email}%"))
    customer = db.session.execute(query).scalars().first()
    print(customer)
    return customer_schema.jsonify(customer), 200
                            




