from datetime import datetime, timedelta, timezone
from flask import request, jsonify
from functools import wraps
import jwt
import os


SECRET_KEY = os.environ.get("SECRET_KEY") or "super secret secrets"
# SECRET_KEY = ogdpro4ZVLwTMX/zUadt45GziZYMX81oKXHWf3Wq8pj6CPZ/beceSxUF00szUm7oeRbfuBByfEowRGMrR141kw==


def encode_token(mechanic_id):  # using unique pieces of info to make our tokens user specific
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=2, hours=0),  # setting the expiration time to an hour past now (change later)
        "iat": datetime.now(timezone.utc),  # issued at time
        "sub": str(mechanic_id) # This needs to be a string or the token will be malformd and wont be able to be decoded
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

    


def token_required(f):  # token required decorator: takes (f) usually route handler function as an argument and uses it to check if request has valid token
    @wraps(f)
    def decorated(*args, **kwargs):  # ensures the wrapped function (decorated) retains name and docstring of the original function (f)
        token = None # initalizes token to none and checks if authorization header is present in request. if so splits header to extract actual token
        auth_header = request.headers.get("Authorization") 

        #look for token in the request headers
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

            if not token: # if no token found returns JSON response with an error message and 401
                return jsonify({"message": "Token is missing!"}), 401

            try:  # tries to decode token using secret_key and specific algorithm, if successful it extracts user id from decoded data
                # Decode the token
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                request.mechanic_id = int(data['sub']) # Fetch the mechanic id
                print(f"decoded token data: {data}")
                

            except jwt.ExpiredSignatureError:  # if token has expired or invalid caches exceptions and returns corresponding error message
                return jsonify({"message": "Token has expired!"}), 401
            except jwt.InvalidTokenError as e: # if token is invalid or malformed caches exceptions and returns corresponding error message
                return jsonify({"message": "Invalid token!"}), 401
            
            return f(*args, **kwargs)  # if token is valid calls original function (f) passing the userid and any other args
        else:
            return jsonify({"message": "You must be looged in to access this function."}), 400


    return decorated
