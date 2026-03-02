from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()


# =====================================================
# USER MODEL
# =====================================================
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False, default="buyer")

    is_approved = db.Column(db.Boolean, default=True)
    requested_role = db.Column(db.String(20), nullable=True)

    products = relationship(
        "Product",
        backref="seller",
        lazy=True,
        cascade="all, delete"
    )

    purchases = relationship(
        "Transaction",
        backref="buyer",
        lazy=True,
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<User {self.username}>"


# =====================================================
# PRODUCT MODEL (FIXED VERSION)
# =====================================================
class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), nullable=False)

    # FIX 1: Made nullable (since you're not sending file_url)
    file_url = db.Column(db.String(250), nullable=True)

    # Image for display
    image_url = db.Column(db.String(500), nullable=True)

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    transactions = relationship(
        "Transaction",
        backref="product",
        lazy=True,
        cascade="all, delete"
    )

    # FIX 2: Removed UniqueConstraint to avoid DB crash
    # Duplicate prevention is already handled in backend logic

    def __repr__(self):
        return f"<Product {self.title}>"


# =====================================================
# TRANSACTION MODEL
# =====================================================
class Transaction(db.Model):
    __tablename__ = "transaction"

    id = db.Column(db.Integer, primary_key=True)

    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False
    )

    amount = db.Column(db.Float, nullable=True)

    status = db.Column(
        db.String(20),
        nullable=False,
        default="completed"
    )

    timestamp = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<Transaction {self.id}>"


# =====================================================
# CART MODEL
# =====================================================
class Cart(db.Model):

    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)

    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False
    )

    quantity = db.Column(db.Integer, default=1)

    product = db.relationship("Product")