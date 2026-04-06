from flask import Blueprint, session, redirect, render_template, request
from db import get_db
from datetime import datetime

orders = Blueprint("orders", __name__)

@orders.route("/orders")
def orders_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/register")

    db = get_db()
    with db.cursor() as cur:
        cur.execute("""
            SELECT id, total_price, status, created_at
            FROM orders
            WHERE user_id=%s
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cur.fetchall()

    orders_list = []
    for row in rows:
        created_at = row["created_at"]
        if not isinstance(created_at, datetime):
            created_at = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
        orders_list.append({
            "id": row["id"],
            "total_price": row["total_price"],
            "status": row["status"],
            "created_at": created_at
        })

    return render_template("orders.html", orders=orders_list)

@orders.route("/order_items/<int:order_id>")
def order_items(order_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/register")

    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT user_id FROM orders WHERE id=%s", (order_id,))
        order = cur.fetchone()
        if not order or order["user_id"] != user_id:
            return redirect("/orders")

        cur.execute("""
            SELECT p.name, oi.price, oi.quantity
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            WHERE oi.order_id=%s
        """, (order_id,))
        rows = cur.fetchall()

    items = [{"name": r["name"], "price": float(r["price"]), "quantity": r["quantity"]} for r in rows]

    return render_template("order_items.html", items=items)

@orders.route("/create_order", methods=["POST"])
def create_order():
    user_id = session.get("user_id")
    cart = session.get("cart", [])
    if not user_id:
        return redirect("/register")
    if not cart:
        return redirect("/cart")

    country = request.form.get("country")
    city = request.form.get("city")
    street = request.form.get("street")
    postal_code = request.form.get("postal_code")

    db = get_db()
    with db.cursor() as cur:
        cur.execute("INSERT INTO addresses(user_id,country,city,street,postal_code) VALUES(%s,%s,%s,%s,%s)",
                    (user_id, country, city, street, postal_code))
        address_id = cur.lastrowid

        total = 0
        for pid in cart:
            cur.execute("SELECT price FROM products WHERE id=%s", (pid,))
            product = cur.fetchone()
            if product:
                total += float(product["price"])

        cur.execute("INSERT INTO orders(user_id,total_price,status) VALUES(%s,%s,'new')", (user_id, total))
        order_id = cur.lastrowid

        for pid in cart:
            cur.execute("SELECT price FROM products WHERE id=%s", (pid,))
            product = cur.fetchone()
            if product:
                cur.execute("INSERT INTO order_items(order_id,product_id,quantity,price) VALUES(%s,%s,%s,%s)",
                            (order_id, pid, 1, product["price"]))

        db.commit()
        session["cart"] = []

    return redirect("/orders")

@orders.route("/checkout")
def checkout():
    user_id = session.get("user_id")
    cart = session.get("cart", [])
    if not user_id:
        return redirect("/register")
    if not cart:
        return redirect("/cart")

    cart_items = []
    total = 0
    db = get_db()
    with db.cursor() as cur:
        for pid in cart:
            cur.execute("SELECT id,name,price,image FROM products WHERE id=%s", (pid,))
            product = cur.fetchone()
            if product:
                item = {
                    "id": product["id"],
                    "name": product["name"],
                    "price": float(product["price"]),
                    "image": product["image"],
                    "quantity": 1
                }
                cart_items.append(item)
                total += item["price"]

    return render_template("checkout.html", cart_items=cart_items, total_price=total)
