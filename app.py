from flask import Flask, render_template, g
from config import *
from db import get_db, close_db
from admin import init_admin
from routes.auth import auth
from routes.products import products
from routes.cart import cart
from routes.orders import orders

# -------------------- Создание Flask приложения --------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY

# -------------------- Инициализация админки --------------------
init_admin(app)

# -------------------- Регистрация Blueprints --------------------
app.register_blueprint(auth)
app.register_blueprint(products)
app.register_blueprint(cart)
app.register_blueprint(orders)

# -------------------- Закрытие соединения с БД после запроса --------------------
@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)

# -------------------- Маршруты --------------------
@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/articles")
def articles():
    return render_template("articles.html")

@app.route("/article")
def article():
    return render_template("article.html")

@app.route("/")
def index():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM users")  # пример запроса
        rows = cursor.fetchall()
    return render_template("index.html", users=rows)

# -------------------- Запуск приложения --------------------
if __name__ == "__main__":
    print(app.url_map)  # вывод всех маршрутов для проверки
