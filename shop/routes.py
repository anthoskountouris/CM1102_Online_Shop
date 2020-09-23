from flask import render_template, url_for, request, redirect, flash, session
from sqlalchemy import desc, asc
from shop import app, db
from shop.models import User, Books, Reviews, Wishlist, Purchases, Purchased_items
from shop.forms import RegistrationForm, LoginForm, checkoutForm, reviewForm
from flask_login import login_user, logout_user, current_user
from datetime import datetime
import pymysql


def purge_cart():
    # Empty the cart if it is active
    if ("cart" in session):
        session["cart"] = []


def is_cart_valid():
    # Checks if the entire cart is elligible for purchase, returns bool
    # (cart has items and ALL items in stock at required quantity)
    valid = True
    if ("cart" not in session or len(session["cart"]) == 0):
        # Cart empty
        flash("There are no items in your cart.")
        valid = False
    else:
        # Cart has items
        no_duplicates = set(session["cart"])
        for item_id in no_duplicates:
            item = Books.query.get_or_404(item_id)
            if (item.stock_level < 1):
                flash(f"{item.title} is out of stock and cannot be purchased.")
                valid = False
            elif (item.stock_level < session["cart"].count(item_id)):
                flash(
                    f"We only have {item.stock_level} {'copy' if item.stock_level == 1 else 'copies'} of {item.title} in stock.")
                valid = False
            else:
                pass
    return valid


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.context_processor
def inject_header_quantities():
    # get cart quantity from session
    if ("cart" not in session):
        cq = 0
    else:
        cq = len(session["cart"])
    # get wishlist quantity from db
    if (current_user.is_authenticated):
        wish = Wishlist.query.filter_by(wishlist_user_id=current_user.id).all()
        wq = len(wish)
    else:
        wq = None
    return dict(cart_quantity=cq, wishlist_quantity=wq)


@app.route("/")
def home():
    sort = request.args.get('sort', default='1', type=int)
    if (sort == 1):
        books = Books.query.order_by(Books.price)
    else:
        books = Books.query.order_by(Books.price.desc())
    return render_template('home.html', books=books)


@app.route("/user")
def user():
    if (current_user.is_authenticated):
        user_purchases = Purchases.query.filter_by(
            purchase_user_id=current_user.id).all()
        user_reviews = Reviews.query.filter_by(
            reviewer_id=current_user.id).all()
        return render_template('user.html', purchases=user_purchases, reviews=user_reviews)
    else:
        flash("You are not logged in.")
        return redirect(url_for("login"))


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if (form.validate_on_submit()):
        user = User(username=form.username.data,
                    email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if (form.validate_on_submit()):
        user = User.query.filter_by(email=form.email.data).first()
        if (user is not None and user.verify_password(form.password.data)):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('home'))
        flash('Invalid email address or password.')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    purge_cart()
    flash('Logout successful.')
    return redirect(url_for('home'))


@app.route("/viewinfo", methods=['GET', 'POST'])
def view():
    id = request.args.get('id', default='0', type=int)
    # default 0 purposely causes 404 if book ID not specified
    review_sort_mode = request.args.get('sort', default='0', type=int)
    book = Books.query.get_or_404(id)
    if (review_sort_mode == 1):
        # Sort reviews by first posted
        revs = Reviews.query.filter_by(
            book_about=book.book_id).order_by(Reviews.timestamp).all()
    elif (review_sort_mode == 2):
        # Sort reviews by highest rating
        revs = Reviews.query.filter_by(
            book_about=book.book_id).order_by(Reviews.star_rating.desc()).all()
    elif (review_sort_mode == 3):
        # Sort reviews by lowest rating
        revs = Reviews.query.filter_by(
            book_about=book.book_id).order_by(Reviews.star_rating).all()
    else:
        # Sort reviews by most recently posted
        revs = Reviews.query.filter_by(
            book_about=book.book_id).order_by(Reviews.timestamp.desc()).all()
    form = reviewForm()
    if ((current_user.is_authenticated) and (Reviews.query.filter_by(book_about=book.book_id, reviewer_id=current_user.id).scalar() is None)):
        has_not_reviewed = True
    else:
        has_not_reviewed = False

    if (request.method == "POST" and form.validate_on_submit()):
        new_review = Reviews(book_about=id,
                             reviewer_id=current_user.id,
                             timestamp=datetime.utcnow(),
                             star_rating=form.star_rating.data,
                             content=form.content.data)
        db.session.add(new_review)
        db.session.commit()

        flash('Review submitted')
        return redirect(url_for('view', id=id, sort=review_sort_mode, _anchor='viewitem-reviews-base'))

    return render_template('viewinfo.html', book=book, revs=revs, form=form, has_not_reviewed=has_not_reviewed)


@app.route('/delete_review/<int:book_id>')
def delete_review(book_id):
    if (current_user.is_authenticated):
        own_review = Reviews.query.filter_by(
            book_about=book_id, reviewer_id=current_user.id).first()
        if (own_review is None):
            flash("You have not reviewed this book")
        else:
            db.session.delete(own_review)
            db.session.commit()
            flash("Your review has been deleted.")
    else:
        flash("Please log in to delete your reviews.")
    return redirect(url_for('view', id=book_id))


@app.route('/wishlist/')
def wishlist():
    if (current_user.is_authenticated):
        wishlist_sort_mode = request.args.get('sort', default='0', type=int)
        if (wishlist_sort_mode == 0):
            items = Wishlist.query.filter_by(
                wishlist_user_id=current_user.id).join(Books, Wishlist.item_details).order_by(Books.price.desc()).all()
        else:
            items = Wishlist.query.filter_by(
                wishlist_user_id=current_user.id).join(Books, Wishlist.item_details).order_by(Books.price).all()
        return render_template('wishlist.html', wishlist_items=items)
    else:
        flash("Please log in to create a wishlist")
        return redirect(url_for('home'))


@app.route('/add_to_wishlist/<int:book_id>')
def add_to_wishlist(book_id):
    if (current_user.is_authenticated):
        list_elements = Wishlist.query.filter_by(
            wishlist_user_id=current_user.id, wishlist_item_id=book_id).first()
        if (list_elements is not None):  # user/item combo in db
            flash("This item is already in your wishlist")
        else:
            new_wishlist_item = Wishlist(wishlist_user_id=current_user.id,
                                         wishlist_item_id=book_id)
            db.session.add(new_wishlist_item)
            db.session.commit()
            flash("The item has been added to your wishlist")
    else:
        pass
    return redirect(url_for('wishlist'))


@app.route('/remove_from_wishlist/<int:book_id>')
def remove_from_wishlist(book_id):
    if (current_user.is_authenticated):
        list_elements = Wishlist.query.filter_by(
            wishlist_user_id=current_user.id, wishlist_item_id=book_id).first()
        if (list_elements is not None):  # user/item combo in db
            db.session.delete(list_elements)
            db.session.commit()
            flash("The item has been removed from your wishlist")
        else:
            flash("This item is not in your wishlist")
    else:
        pass
    return redirect(url_for('wishlist'))


@app.route("/cart", methods=['GET', 'POST'])
def cart():
    if ("cart" not in session):
        session["cart"] = []
    cart_items = session["cart"]
    cart = {}
    total_price = 0
    total_quantity = 0
    for item in cart_items:
        book = Books.query.get_or_404(item)
        total_price += book.price
        if (book.book_id in cart):
            cart[book.book_id]["quantity"] += 1
        else:
            cart[book.book_id] = {"quantity": 1,
                                  "title": book.title, "price": book.price}
    total_quantity = len(cart_items)
    return render_template("cart.html", display_cart=cart, total_price=total_price, total_quantity=total_quantity)


@app.route("/add_to_cart/<int:book_id>")
def add_to_cart(book_id):
    if ("cart" not in session):
        session["cart"] = []
    item_to_add = Books.query.get_or_404(book_id)
    session["cart"].append(book_id)
    flash(f"{item_to_add.title} has been added to your shopping cart.")
    session.modified = True
    return redirect(url_for('cart'))


@app.route("/remove_from_cart/<int:book_id>", methods=['GET', 'POST'])
def remove_from_cart(book_id):
    if ("cart" not in session):
        session["cart"] = []
    session["cart"].remove(book_id)
    flash("Item removed from your cart.")
    session.modified = True
    return redirect(url_for('cart'))


@app.route("/empty_cart")
def empty_cart():
    purge_cart()
    return redirect(url_for('cart'))


@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    form = checkoutForm()
    if (not is_cart_valid()):
        return redirect(url_for('cart'))
    else:
        if (request.method == "POST" and form.validate_on_submit()):
            # Enter purchase into purchases table
            ship_address = f"{form.ship_name.data}, {form.ship_street.data}, {form.ship_town.data}, {form.ship_postcode.data}"
            payment = f"{str(form.card_number.data).zfill(16)}, {str(form.card_ccv.data).zfill(3)}"
            new_purchase = Purchases(purchase_user_id=(current_user.id if current_user.is_authenticated else 0),
                                     purchase_timestamp=datetime.utcnow(),
                                     purchase_ship_to=ship_address,
                                     purchase_payment=payment)
            db.session.add(new_purchase)
            db.session.commit()

            # Enter purchased items (from cart session) into relational table
            no_duplicates = set(session["cart"])
            for item in no_duplicates:
                new_item = Purchased_items(purchase_id=new_purchase.purchase_id,
                                           item_id=item,
                                           quantity=session["cart"].count(item))
                db.session.add(new_item)
            db.session.commit()

            # Increment purchase counter and decrement stock for each item purchased
            for item in session["cart"]:
                item_data = Books.query.get_or_404(item)
                item_data.purchase_counter += 1
                item_data.stock_level -= 1
                db.session.commit()

            flash("Purchase successful")
            purge_cart()
            return redirect(url_for('home'))
        else:
            return render_template('checkout.html', form=form)
