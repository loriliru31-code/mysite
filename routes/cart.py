from flask import Blueprint, session, jsonify, render_template
from db import get_db
from collections import Counter

cart = Blueprint("cart", __name__)

@cart.route("/cart")
def view_cart():
    cart_session = session.get("cart", [])
    cart_count = Counter(cart_session) 
    products = []
    total_price = 0

    db = get_db()  # получаем соединение
    with db.cursor() as cur:
        for product_id, qty in cart_count.items():
            cur.execute("SELECT id, name, price, image FROM products WHERE id=%s", (product_id,))
            row = cur.fetchone()
            if row:
                item = {
                    "id": row["id"],
                    "name": row["name"],
                    "price": float(row["price"]),
                    "quantity": qty,
                    "image": row["image"] or "img/default_product.jpg"
                }
                products.append(item)
                total_price += item["price"] * item["quantity"]

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

    cart_session = session.get("cart", [])
    cart_count = Counter(cart_session)
    total_price = 0

    db = get_db()
    with db.cursor() as cur:
        for pid, qty in cart_count.items():
            cur.execute("SELECT price FROM products WHERE id=%s", (pid,))
            row = cur.fetchone()
            if row:
                total_price += float(row["price"]) * qty

    return jsonify({"success": True, "cart_count": len(cart_session), "total_price": total_price})\
