from datetime import datetime
from shop import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Books(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(5000), nullable=False)
    isbn_number = db.Column(db.String(50), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_file = db.Column(db.String(30), nullable=False,
                           default='default.jpg')
    purchase_counter = db.Column(db.Integer, nullable=False)
    stock_level = db.Column(db.Integer, nullable=False)
    where_bought = db.relationship(
        'Purchased_items', backref='item_details', lazy='dynamic')
    where_wishlisted = db.relationship(
        'Wishlist', backref='item_details', lazy='dynamic')
    item_reviews = db.relationship(
        'Reviews', backref='item_details', lazy='dynamic')

    def __repr__(self):
        return f"Books('{self.title}', '{self.description}', '{self.price}', '{self.stock_level}')"


class Reviews(db.Model):
    book_about = db.Column(db.Integer, db.ForeignKey(
        'books.book_id'), primary_key=True)
    reviewer_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime(), nullable=False)
    star_rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(5000), nullable=False)

    def __repr__(self):
        return f"Reviews('{self.book_about}',  '{self.reviewer_id}', '{self.timestamp}', '{self.star_rating}', '{self.content}')"


class Wishlist(db.Model):
    wishlist_user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), primary_key=True)
    wishlist_item_id = db.Column(
        db.Integer, db.ForeignKey('books.book_id'), primary_key=True)

    def __repr__(self):
        return f"Wishlist('{self.wishlist_user_id}', '{self.wishlist_item_id}')"


class Purchases(db.Model):
    purchase_id = db.Column(db.Integer, primary_key=True)
    purchase_user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    purchase_timestamp = db.Column(db.Integer, nullable=False)
    purchase_ship_to = db.Column(db.String(200), nullable=False)
    purchase_payment = db.Column(db.String(25), nullable=False)
    items_bought = db.relationship(
        'Purchased_items', backref='order_details', lazy='dynamic')

    def __repr__(self):
        return f"Purchases('{self.purchase_id}', '{self.purchase_user_id}', '{self.purchase_timestamp}', '{self.purchase_ship_to}', '{self.purchase_payment}')"


class Purchased_items(db.Model):
    purchase_id = db.Column(db.Integer, db.ForeignKey(
        'purchases.purchase_id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey(
        'books.book_id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Purchased_items('{self.purchase_id}', '{self.item_id}', '{self.quantity})"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    purchases = db.relationship('Purchases', backref='buyer', lazy='dynamic')
    reviews_left = db.relationship(
        'Reviews', backref='reviewer_details', lazy='dynamic')
    items_wishlisted = db.relationship(
        'Wishlist', backref='wishlister', lazy='dynamic')

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
