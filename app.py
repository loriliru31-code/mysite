from flask import Flask, render_template
from config import *
from db import mysql
from admin import init_admin
from routes.auth import auth
from routes.products import products
from routes.cart import cart
from routes.orders import orders

# создаём Flask приложение
app = Flask(__name__)

app.config["MYSQL_HOST"] = MYSQL_HOST
app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB
app.secret_key = SECRET_KEY

init_admin(app)
mysql.init_app(app)

app.register_blueprint(auth)     
app.register_blueprint(products)  
app.register_blueprint(cart)     
app.register_blueprint(orders)  

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
    return render_template("index.html")

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)