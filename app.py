from flask import Flask, render_template, jsonify
from config import Config
from models import db, User
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

# ===============================
# Import Blueprints
# ===============================

from routes.auth import auth_bp
from routes.products import products_bp
from routes.transactions import transactions_bp
from routes.admin import admin_bp
from routes.cart import cart_bp

# ===============================
# Create Flask App
# ===============================

app = Flask(__name__)

app.config.from_object(Config)


# ===============================
# Initialize Extensions
# ===============================

db.init_app(app)

jwt = JWTManager(app)


# ===============================
# Register Blueprints
# ===============================

# AUTH API
app.register_blueprint(auth_bp, url_prefix="/api/auth")

# PRODUCTS (API + UI handled inside blueprint)
app.register_blueprint(products_bp, url_prefix="/api/products")

# TRANSACTIONS API
app.register_blueprint(transactions_bp, url_prefix="/api/transactions")

# ADMIN API
app.register_blueprint(admin_bp, url_prefix="/api/admin")

# CART API
app.register_blueprint(cart_bp)

# ===============================
# ERROR HANDLERS
# ===============================

@app.errorhandler(404)
def not_found(e):

    return jsonify({
        "error": "Resource not found"
    }), 404


@app.errorhandler(500)
def server_error(e):

    return jsonify({
        "error": "Internal server error"
    }), 500


@app.errorhandler(IntegrityError)
def handle_integrity_error(e):

    db.session.rollback()

    return jsonify({
        "error": "Database constraint violation"
    }), 400


# ===============================
# FRONTEND ROUTES (UI)
# ===============================

@app.route("/")
def home():

    return render_template("index.html")


@app.route("/login")
def login_page():

    return render_template("login.html")


@app.route("/register")
def register_page():

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():

    return render_template("dashboard.html")


@app.route("/buyer/dashboard")
def buyer_dashboard():

    return render_template("buyer_dashboard.html")

@app.route("/cart")
def cart_page():

    return render_template("cart.html")

@app.route("/seller/dashboard")
def seller_dashboard():

    return render_template("add_product.html")


@app.route("/admin/dashboard")
def admin_dashboard():

    return render_template("admin_dashboard.html")


# ===============================
# MARKETPLACE PAGE (UI FIX)
# ===============================
@app.route("/products/marketplace")
def marketplace_page():

    from models import Product

    products = Product.query.order_by(Product.id.desc()).all()

    return render_template("marketplace.html", products=products)

# ===============================
# INITIALIZE DATABASE
# ===============================

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        # Create default admin
        existing_admin = User.query.filter_by(
            email="admin@forgehub.com"
        ).first()

        if not existing_admin:

            admin_user = User(
                username="admin",
                email="admin@forgehub.com",
                password=generate_password_hash("admin123"),
                role="admin",
                is_approved=True
            )

            db.session.add(admin_user)
            db.session.commit()

            print("✅ Default admin created")


    app.run(debug=True)