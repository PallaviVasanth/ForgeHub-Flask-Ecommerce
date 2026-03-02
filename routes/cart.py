from flask import Blueprint, jsonify, request
from models import db, Cart, Product
from flask_jwt_extended import jwt_required, get_jwt_identity


# Blueprint
cart_bp = Blueprint(
    "cart_bp",
    __name__,
    url_prefix="/api/cart"
)


# =====================================================
# ADD TO CART
# =====================================================
@cart_bp.route("/add/<int:product_id>", methods=["POST"])
@jwt_required()
def add_to_cart(product_id):

    try:

        user_id = int(get_jwt_identity())

        product = Product.query.get(product_id)

        if not product:
            return jsonify({"error": "Product not found"}), 404


        existing = Cart.query.filter_by(
            buyer_id=user_id,
            product_id=product_id
        ).first()


        if existing:
            existing.quantity += 1
        else:
            item = Cart(
                buyer_id=user_id,
                product_id=product_id,
                quantity=1
            )
            db.session.add(item)


        db.session.commit()

        return jsonify({"message": "Added to cart successfully"}), 200


    except Exception as e:

        print("Cart error:", e)

        return jsonify({"error": "Failed to add to cart"}), 500



# =====================================================
# GET CART ITEMS
# =====================================================
@cart_bp.route("/", methods=["GET"])
@jwt_required()
def get_cart():

    user_id = int(get_jwt_identity())

    items = Cart.query.filter_by(buyer_id=user_id).all()

    result = []

    for item in items:

        product = Product.query.get(item.product_id)

        total = product.price * item.quantity

        result.append({

            "id": item.id,

            "product_id": product.id,

            "title": product.title,

            "price": product.price,

            "quantity": item.quantity,

            "image_url": product.image_url,   # ✅ REQUIRED

            "total": total                    # ✅ REQUIRED

        })

    return jsonify(result), 200


# =====================================================
# UPDATE QUANTITY (FIXED & REQUIRED)
# =====================================================
@cart_bp.route("/update/<int:item_id>", methods=["POST"])
@jwt_required()
def update_quantity(item_id):

    try:

        user_id = int(get_jwt_identity())

        data = request.get_json()

        change = int(data.get("change", 0))


        item = Cart.query.filter_by(
            id=item_id,
            buyer_id=user_id
        ).first()


        if not item:
            return jsonify({"error": "Item not found"}), 404


        new_quantity = item.quantity + change


        if new_quantity <= 0:
            db.session.delete(item)
        else:
            item.quantity = new_quantity


        db.session.commit()

        return jsonify({"message": "Quantity updated successfully"}), 200


    except Exception as e:

        print("Cart update error:", e)

        return jsonify({"error": "Failed to update quantity"}), 500



# =====================================================
# REMOVE ITEM FROM CART
# =====================================================
@cart_bp.route("/remove/<int:item_id>", methods=["DELETE"])
@jwt_required()
def remove_from_cart(item_id):

    try:

        user_id = int(get_jwt_identity())

        item = Cart.query.filter_by(
            id=item_id,
            buyer_id=user_id
        ).first()

        if not item:
            return jsonify({"error": "Item not found"}), 404


        db.session.delete(item)

        db.session.commit()

        return jsonify({"message": "Item removed"}), 200


    except Exception as e:

        print("Cart remove error:", e)

        return jsonify({"error": "Failed to remove item"}), 500
    
# =====================================================
# CHECKOUT CART
# =====================================================
@cart_bp.route("/checkout", methods=["POST"])
@jwt_required()
def checkout():

    try:

        user_id = int(get_jwt_identity())

        items = Cart.query.filter_by(
            buyer_id=user_id
        ).all()

        if not items:
            return jsonify({
                "error": "Cart is empty"
            }), 400


        total_amount = 0

        for item in items:

            product = Product.query.get(item.product_id)

            if not product:
                continue

            total_amount += product.price * item.quantity


        # Clear cart after checkout
        for item in items:
            db.session.delete(item)

        db.session.commit()


        return jsonify({

            "message": "Checkout successful",

            "total": total_amount

        }), 200


    except Exception as e:

        print("Checkout error:", e)

        return jsonify({
            "error": "Checkout failed"
        }), 500