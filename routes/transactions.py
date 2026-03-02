from flask import Blueprint, jsonify
from models import db, Product, Transaction
from flask_jwt_extended import jwt_required, get_jwt_identity
from routes.auth import role_required

transactions_bp = Blueprint("transactions", __name__)


# ==========================================
# BUY PRODUCT (BUYER ONLY)
# ==========================================
@transactions_bp.route("/buy/<int:product_id>", methods=["POST"])
@role_required("buyer")
def buy_product(product_id):
    buyer_id = int(get_jwt_identity())

    product = Product.query.get(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Prevent seller from buying own product
    if product.seller_id == buyer_id:
        return jsonify({"error": "You cannot buy your own product"}), 403

    # Prevent duplicate purchase
    existing_transaction = Transaction.query.filter_by(
        buyer_id=buyer_id,
        product_id=product_id
    ).first()

    if existing_transaction:
        return jsonify({"error": "You have already purchased this product"}), 400

    new_transaction = Transaction(
        buyer_id=buyer_id,
        product_id=product_id
    )

    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({"message": "Purchase successful!"}), 200


# ==========================================
# VIEW ALL TRANSACTIONS (ADMIN ONLY)
# ==========================================
@transactions_bp.route("/admin", methods=["GET"])
@role_required("admin")
def view_all_transactions():
    transactions = Transaction.query.all()

    result = []
    for t in transactions:
        result.append({
            "id": t.id,
            "buyer_id": t.buyer_id,
            "product_id": t.product_id,
            "timestamp": str(t.timestamp)
        })

    return jsonify(result), 200


# ==========================================
# VIEW MY PURCHASES (BUYER ONLY)
# ==========================================
@transactions_bp.route("/my", methods=["GET"])
@role_required("buyer")
def view_my_transactions():
    buyer_id = int(get_jwt_identity())

    transactions = Transaction.query.filter_by(buyer_id=buyer_id).all()

    result = []
    for t in transactions:
        result.append({
            "id": t.id,
            "product_id": t.product_id,
            "timestamp": str(t.timestamp)
        })

    return jsonify(result), 200