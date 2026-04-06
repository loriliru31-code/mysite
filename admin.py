from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, session

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    name = db.Column(db.String(255))
    role = db.Column(db.String(10))

    def __str__(self):
        return self.email

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(100))
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    category_id = db.Column(db.Integer)
    image = db.Column(db.String(255))

    def __str__(self):
        return self.name


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    parent_id = db.Column(db.Integer)

    def __str__(self):
        return self.name


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    status = db.Column(db.String(20))
    total_price = db.Column(db.Float)


# --- ЗАЩИТА АДМИНКИ ---
class AdminModelView(ModelView):
    def is_accessible(self):
        return session.get("role") == "admin"

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/admin/login")


def init_admin(app):
    # ✅ проверяем, есть ли уже конфиг
    try:
        db_uri = (
            f"mysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}"
            f"@{app.config['MYSQL_HOST']}/{app.config['MYSQL_DB']}"
        )
    except KeyError:
        raise Exception("❌ MYSQL конфиг не найден. Проверь порядок init_admin(app) в app.py")

    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    admin = Admin(app, name="Shop Admin")

    admin.add_view(AdminModelView(User, db.session))
    admin.add_view(AdminModelView(Product, db.session))
    admin.add_view(AdminModelView(Category, db.session))
    admin.add_view(AdminModelView(Order, db.session))

    return admin