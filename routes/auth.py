from flask import Blueprint, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from functools import wraps


auth_bp = Blueprint("auth", __name__)


# ========================
# REGISTER ROUTE
# ========================
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "buyer")

    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400


    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400


    hashed_password = generate_password_hash(password)


    # BUYER → auto approved
    if role == "buyer":

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            role="buyer",
            is_approved=True
        )


    # SELLER → needs approval
    elif role == "seller":

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            role="buyer",  # temporary
            requested_role="seller",
            is_approved=False
        )

    else:

        return jsonify({"error": "Invalid role selected"}), 400


    db.session.add(user)
    db.session.commit()


    if role == "seller":

        return jsonify({
            "message": "Seller request submitted. Await admin approval."
        }), 201


    return jsonify({
        "message": "Registration successful"
    }), 201



# ========================
# LOGIN ROUTE
# ========================
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")


    if not email or not password:

        return jsonify({
            "error": "Email and password required"
        }), 400


    user = User.query.filter_by(email=email).first()


    if not user:

        return jsonify({
            "error": "Invalid credentials"
        }), 401


    if not check_password_hash(user.password, password):

        return jsonify({
            "error": "Invalid credentials"
        }), 401


    # Seller approval check
    if user.requested_role == "seller" and not user.is_approved:

        return jsonify({
            "error": "Seller account pending admin approval"
        }), 403


    access_token = create_access_token(
        identity=str(user.id)
    )


    return jsonify({

        "access_token": access_token,

        "role": user.role,

        "username": user.username

    }), 200



# ========================
# CURRENT USER INFO
# ========================
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():

    user_id = get_jwt_identity()

    user = User.query.get(int(user_id))

    if not user:

        return jsonify({
            "error": "User not found"
        }), 404


    return jsonify({

        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role

    }), 200



# ========================
# ROLE REQUIRED DECORATOR
# ========================
def role_required(required_role):

    def wrapper(fn):

        @wraps(fn)
        @jwt_required()

        def decorator(*args, **kwargs):

            user_id = get_jwt_identity()

            user = User.query.get(int(user_id))

            if not user:

                return jsonify({
                    "error": "User not found"
                }), 404


            if user.role != required_role:

                return jsonify({
                    "error": "Access forbidden"
                }), 403


            return fn(*args, **kwargs)


        return decorator


    return wrapper