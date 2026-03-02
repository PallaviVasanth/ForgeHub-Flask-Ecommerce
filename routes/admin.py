from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Product, Transaction
from routes.auth import role_required

admin_bp = Blueprint("admin", __name__)


# ================================
# SELLER REQUESTS
# ================================
@admin_bp.route("/seller-requests", methods=["GET"])
@role_required("admin")
def get_seller_requests():

    pending = User.query.filter_by(
        requested_role="seller",
        is_approved=False
    ).all()

    return jsonify([
        {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
        for user in pending
    ]), 200


# ================================
# APPROVE SELLER
# ================================
@admin_bp.route("/approve-seller/<int:user_id>", methods=["POST"])
@role_required("admin")
def approve_seller(user_id):

    user = User.query.get(user_id)

    if not user or user.requested_role != "seller":
        return {"error": "Invalid seller request"}, 404

    user.role = "seller"
    user.is_approved = True
    user.requested_role = None

    db.session.commit()

    return {"message": "Seller approved successfully"}, 200


# ================================
# REJECT SELLER
# ================================
@admin_bp.route("/reject-seller/<int:user_id>", methods=["POST"])
@role_required("admin")
def reject_seller(user_id):

    user = User.query.get(user_id)

    if not user:
        return {"error": "User not found"}, 404

    db.session.delete(user)
    db.session.commit()

    return {"message": "Seller request rejected"}, 200


# ================================
# VIEW ALL USERS
# ================================
@admin_bp.route("/users", methods=["GET"])
@role_required("admin")
def view_users():

    users = User.query.all()

    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "approved": u.is_approved,
            "requested_role": u.requested_role
        }
        for u in users
    ]), 200


# ================================
# VIEW ALL PRODUCTS
# ================================
@admin_bp.route("/products", methods=["GET"])
@role_required("admin")
def view_products():

    products = Product.query.all()

    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "price": p.price,
            "category": p.category,
            "seller_id": p.seller_id
        }
        for p in products
    ]), 200


# ================================
# VIEW ALL TRANSACTIONS
# ================================
@admin_bp.route("/transactions", methods=["GET"])
@role_required("admin")
def view_transactions():

    transactions = Transaction.query.all()

    return jsonify([
        {
            "id": t.id,
            "buyer_id": t.buyer_id,
            "product_id": t.product_id,
            "timestamp": str(t.timestamp)
        }
        for t in transactions
    ]), 200