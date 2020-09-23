from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'db5821567f7f382d2883960140f805c2da33e9bffd7b78d6'

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c1945047:Team18MySQL@csmysql.cs.cf.ac.uk:3306/c1945047_Team18'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 1
db = SQLAlchemy(app)

from flask_login import LoginManager

login_manager = LoginManager() 
login_manager.init_app(app)

from shop import routes

from flask_admin import Admin
from shop.views import AdminView
from shop.models import User, Books, Reviews, Wishlist, Purchases, Purchased_items
admin = Admin(app,name='Admin panel',template_mode='bootstrap3')
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Books, db.session))
admin.add_view(AdminView(Reviews, db.session))
admin.add_view(AdminView(Purchases, db.session))
admin.add_view(AdminView(Purchased_items, db.session))
admin.add_view(AdminView(Wishlist, db.session))

