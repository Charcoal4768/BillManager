from datetime import datetime
from sqlalchemy import or_
from sqlalchemy import Index, func
from flask_login import UserMixin
from .extensions import db

# A helper class for timestamping, not strictly necessary but good practice
class TimestampMixin(object):
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class User(db.Model, UserMixin, TimestampMixin):
    """
    User model for authentication and login management.
    Inherits from UserMixin to integrate with Flask-Login.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(100))
    addr = db.Column(db.String(200))
    gstno = db.Column(db.String(12), nullable=False)
    # Relationship to stores: a user can have multiple stores
    stores = db.relationship('Store', backref='owner', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

    @classmethod
    def get_all_stores(cls, userid):
        """
        Retrieves all stores associated with a given user ID.
        This is useful for a user dashboard showing all their stores.
        """
        return Store.query.filter_by(user_id=userid).all()

    @classmethod
    def create_user(cls, name, email, phone=None, addr=None, gstno=None, password="None"):
        """
        Creates a new user instance.
        """
        new_user = cls(name=name, email=email, phone=phone, addr=addr, gstno=gstno, password=password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def edit_user(cls, user_id, **kwargs):
        """
        Updates an existing user's information.
        """
        user = cls.query.get(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            db.session.commit()
            return user
        return None

    @classmethod
    def delete_user(cls, user_id):
        """
        Deletes a user and all their associated stores and products.
        """
        user = cls.query.get(user_id)
        if user:
            # Cascading delete should handle this, but it's good to be explicit
            for store in user.stores:
                db.session.delete(store)
            db.session.delete(user)
            db.session.commit()
            return True
        return False

    @classmethod
    def get_by_phone(cls, phone:str):
        return cls.query.filter_by(phone=phone).first()

class Store(db.Model, TimestampMixin):
    """
    Store model, representing a single business entity.
    Each store is owned by a specific user.
    """
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    addr = db.Column(db.String(200))
    gst_no = db.Column(db.String(50))
    owner = db.Column(db.String(150), nullable=False)
    
    # Foreign key to link a store to a user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship to products and bills: a store can have multiple products and bills
    products = db.relationship('Product', backref='store', lazy=True, cascade="all, delete-orphan")
    bills = db.relationship('Bill', backref='store', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Store('{self.name}')"

    @classmethod
    def get_total_products(cls):
        """
        Counts the total number of products across all stores.
        This would be useful for an admin or dashboard view.
        """
        return db.session.query(db.func.count(Product.id)).scalar()

    @classmethod
    def create_store(cls, user_id, name, email, phone=None, addr=None, gst_no=None):
        """
        Creates a new store and links it to a user.
        """
        new_store = cls(user_id=user_id, name=name, email=email, phone=phone, addr=addr, gst_no=gst_no)
        db.session.add(new_store)
        db.session.commit()
        return new_store

    @classmethod
    def edit_store(cls, store_id, **kwargs):
        """
        Updates an existing store's information.
        """
        store = cls.query.get(store_id)
        if store:
            for key, value in kwargs.items():
                setattr(store, key, value)
            db.session.commit()
            return store
        return None

    @classmethod
    def delete_store(cls, store_id):
        """
        Deletes a store and all its associated products.
        """
        store = cls.query.get(store_id)
        if store:
            db.session.delete(store)
            db.session.commit()
            return True
        return False

class Product(db.Model, TimestampMixin):
    """
    Product model, representing an item available for sale in a store.
    """
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    gst_percent = db.Column(db.Integer, nullable=False)
    expire = db.Column(db.DateTime)
    batch = db.Column(db.String(12))
    mrp = db.Column(db.Float, nullable=False)
    
    # Foreign key to link a product to a store
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    __table_args__ = (
        Index('trgm_product_idx', name, batch, postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops', 'batch': 'gin_trgm_ops'}),
    )
    def __repr__(self):
        return f"Product('{self.name}', MRP: {self.mrp}')"
    
    @classmethod
    def search_products(cls, store_id, query):
        """
        Searches for products within a specific store by name or batch number.
        The search is case-insensitive and supports partial matches.
        Limits the results to a maximum of 5.
        """
        # The `%` wildcard is used for partial matching
        search_term = f"%{query}%"
        return cls.query.filter(
            cls.store_id == store_id,
            or_(
                cls.name.ilike(search_term),
                cls.batch.ilike(search_term)
            )
        ).limit(5).all()

    @classmethod
    def full_search_products(cls, store_id, query):
        """
        Performs a comprehensive, fuzzy, full-text search for products
        within a specific store, ranking results by relevance.
        """
        # Ensure the pg_trgm extension is installed and GIN index is in place for performance
        
        # Search for names and batch numbers using pg_trgm's similarity operators
        return cls.query.filter(
            cls.store_id == store_id,
            or_(
                func.similarity(cls.name, query) > 0.3, # Adjust threshold as needed
                func.similarity(cls.batch, query) > 0.3
            )
        ).order_by(
            # Order by highest similarity score first
            func.greatest(func.similarity(cls.name, query), func.similarity(cls.batch, query)).desc()
        ).all()

    @classmethod
    def create_product(cls, store_id, name, quantity, gst_percent, mrp, expire=None, batch=None):
        """
        Creates a new product instance and links it to a store.
        """
        new_product = cls(
            store_id=store_id,
            name=name,
            quantity=quantity,
            gst_percent=gst_percent,
            mrp=mrp,
            expire=expire,
            batch=batch
        )
        db.session.add(new_product)
        db.session.commit()
        return new_product

    @classmethod
    def edit_product(cls, product_id, **kwargs):
        """
        Updates an existing product's information.
        """
        product = cls.query.get(product_id)
        if product:
            for key, value in kwargs.items():
                setattr(product, key, value)
            db.session.commit()
            return product
        return None

    @classmethod
    def delete_product(cls, product_id):
        """
        Deletes a product from the database.
        """
        product = cls.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return True
        return False

# New models for billing functionality
class Bill(db.Model, TimestampMixin):
    """
    Bill model, representing a single customer invoice.
    It links to a specific store and contains billing details.
    """
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    doctor_name = db.Column(db.String(100))
    billing_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Store information at the time of billing to preserve it
    store_name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(150), nullable=False)
    store_gst_no = db.Column(db.String(50))
    store_addr = db.Column(db.String(200))
    store_phone = db.Column(db.String(20))

    # Foreign key to link a bill to a store
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    
    # A relationship to the BillItem table to get all products on this bill
    items = db.relationship('BillItem', backref='bill', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Bill(ID: {self.id}, Store: {self.store_name}, Date: {self.billing_date.strftime('%Y-%m-%d')})"

class BillItem(db.Model):
    """
    BillItem model, representing a single product line item on a bill.
    This acts as a junction table between Bill and Product to store
    transaction-specific data like quantity, price, and discounts.
    """
    __tablename__ = 'bill_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    discount_percent = db.Column(db.Float, nullable=False, default=0.0)
    gst_percent = db.Column(db.Float, nullable=False, default=0.0)
    total_price = db.Column(db.Float, nullable=False)
    
    # Foreign keys to link the bill item to its bill and product
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Relationship to the product
    product = db.relationship('Product')

    def __repr__(self):
        return f"BillItem(Product ID: {self.product_id}, Quantity: {self.quantity})"