from flask import Blueprint, session, jsonify, render_template
from db import mysql
from collections import Counter

cart = Blueprint("cart", __name__)

@cart.route("/cart")
def view_cart():
    cart_session = session.get("cart", [])
    cart_count = Counter(cart_session) 
    products = []
    total_price = 0

    cur = mysql.connection.cursor()

    for product_id, qty in cart_count.items():
        cur.execute("SELECT id, name, price, image FROM products WHERE id=%s", (product_id,))
        row = cur.fetchone()
        if row:
            item = {
                "id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "quantity": qty,
                "image": row[3] or "img/default_product.jpg"
            }
            products.append(item)
            total_price += item["price"] * item["quantity"]

    cur.close()

    return render_template("cart.html",
                           cart_items=products,
                           total_price=total_price)


# ---------------- Добавление в корзину (AJAX) ----------------
@cart.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(product_id)
    session.modified = True
    cart_count = len(session["cart"])
    return jsonify({"success": True, "cart_count": cart_count})


# ---------------- Удаление из корзины ----------------
@cart.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    if "cart" in session and product_id in session["cart"]:
        session["cart"].remove(product_id)
        session.modified = True

    # пересчитываем корзину и сумму
    cart_session = session.get("cart", [])
    cart_count = Counter(cart_session)
    total_price = 0
    cur = mysql.connection.cursor()
    for pid, qty in cart_count.items():
        cur.execute("SELECT price FROM products WHERE id=%s", (pid,))
        row = cur.fetchone()
        if row:
            total_price += float(row[0]) * qty
    cur.close()

    return jsonify({"success": True, "cart_count": len(cart_session), "total_price": total_price})