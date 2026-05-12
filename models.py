from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

class Branch(db.Model):
    __tablename__ = 'branches'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255))
    users = db.relationship('User', backref='branch', lazy=True)
    products = db.relationship('Product', backref='branch', lazy=True)
    purchases = db.relationship('Purchase', backref='branch', lazy=True)
    sales = db.relationship('Sale', backref='branch', lazy=True)
    transfers_from = db.relationship('StockTransfer', foreign_keys='StockTransfer.from_branch_id', backref='from_branch', lazy=True)
    transfers_to = db.relationship('StockTransfer', foreign_keys='StockTransfer.to_branch_id', backref='to_branch', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    totp_secret = db.Column(db.String(32), nullable=True)   # <-- NEW: for 2FA
    sales = db.relationship('Sale', backref='user', lazy=True)

    def is_admin(self):
        return self.role and self.role.name == 'admin'
    def is_pharmacist(self):
        return self.role and self.role.name == 'pharmacist'
    def is_cashier(self):
        return self.role and self.role.name == 'cashier'

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    products = db.relationship('Product', backref='supplier', lazy=True)
    purchases = db.relationship('Purchase', backref='supplier', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    barcode = db.Column(db.String(50), unique=True)
    batch_number = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    purchase_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    expiry_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    purchases = db.relationship('Purchase', backref='product', lazy=True)
    sale_items = db.relationship('SaleItem', backref='product', lazy=True)
    expiry_alerts = db.relationship('ExpiryAlert', backref='product', lazy=True)
    transfers = db.relationship('StockTransfer', backref='product', lazy=True)

    @property
    def profit_per_unit(self):
        return round(self.selling_price - self.purchase_price, 2)

class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    buying_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, server_default=db.func.now())

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(10), default='cash')  # cash/mpesa/mixed
    cash_amount = db.Column(db.Float, default=0.0)
    mpesa_amount = db.Column(db.Float, default=0.0)
    amount_received = db.Column(db.Float, default=0.0)
    balance_given = db.Column(db.Float, default=0.0)
    mpesa_code = db.Column(db.String(20))
    receipt_number = db.Column(db.String(50), unique=True)
    sale_date = db.Column(db.DateTime, server_default=db.func.now())
    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')

class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)

class StockTransfer(db.Model):
    __tablename__ = 'stock_transfers'
    id = db.Column(db.Integer, primary_key=True)
    from_branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    to_branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    transfer_date = db.Column(db.DateTime, server_default=db.func.now())

class ExpiryAlert(db.Model):
    __tablename__ = 'expiry_alerts'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    alert_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')