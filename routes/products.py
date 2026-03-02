from flask import Blueprint, request, jsonify
from models import db, Product, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from routes.auth import role_required
from sqlalchemy import func

products_bp = Blueprint(
    "products_bp",
    __name__
)


# ==================================================
# CREATE PRODUCT (SELLER ONLY)
# ==================================================
@products_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("seller")
def create_product():

    data = request.get_json(silent=True)

    if not data:
        data = request.form

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    user_id = int(get_jwt_identity())

    title = data.get("title", "").strip()
    price = data.get("price")

    if title == "" or price is None:
        return jsonify({"error": "Title and price required"}), 400

    try:
        price = float(price)
    except:
        return jsonify({"error": "Invalid price value"}), 400

    existing = Product.query.filter(
        func.lower(Product.title) == title.lower(),
        Product.seller_id == user_id
    ).first()

    if existing:
        return jsonify({"error": "Product already exists"}), 400

    # 🔥 FIX HERE: ensure file_url is always filled
    image_url = data.get("image_url", "")
    file_url = data.get("file_url", image_url)

    product = Product(
        title=title,
        description=data.get("description", ""),
        price=price,
        category=data.get("category", "General"),
        image_url=image_url,
        file_url=file_url,   # 👈 REQUIRED FIX
        seller_id=user_id
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "Product created successfully"}), 201


# ==================================================
# GET ALL PRODUCTS (PUBLIC)
# ==================================================
@products_bp.route("/", methods=["GET"])
def get_all_products():

    products = Product.query.order_by(Product.id.desc()).all()

    result = []

    for p in products:
        result.append({
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "price": p.price,
            "category": p.category,
            "image_url": p.image_url
        })

    return jsonify(result), 200


# ==================================================
# GET SELLER PRODUCTS
# ==================================================
@products_bp.route("/seller/my-products", methods=["GET"])
@jwt_required()
@role_required("seller")
def seller_products():

    user_id = int(get_jwt_identity())

    products = Product.query.filter_by(
        seller_id=user_id
    ).order_by(Product.id.desc()).all()

    result = []

    for p in products:
        result.append({
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "price": p.price,
            "category": p.category,
            "image_url": p.image_url
        })

    return jsonify(result), 200


# ==================================================
# DELETE PRODUCT
# ==================================================
@products_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_product(id):

    product = Product.query.get(id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role == "seller" and product.seller_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Product deleted successfully"}), 200