from flask import Blueprint, session, redirect, render_template, request
from db import mysql
from datetime import datetime

orders = Blueprint("orders", __name__)

# =================== СТРАНИЦА ВСЕХ ЗАКАЗОВ ===================
@orders.route("/orders")
def orders_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/register")

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, total_price, status, created_at
        FROM orders
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cur.fetchall()  # получаем кортежи

    # преобразуем в список словарей для удобства в шаблоне
    orders_list = []
    for row in rows:
        order_id, total_price, status, created_at = row
        # преобразуем created_at в datetime, если нужно
        if not isinstance(created_at, datetime):
            created_at = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
        orders_list.append({
            "id": order_id,
            "total_price": total_price,
            "status": status,
            "created_at": created_at
        })

    return render_template("orders.html", orders=orders_list)


# =================== ПРОСМОТР ТОВАРОВ В ЗАКАЗЕ ===================
@orders.route("/order_items/<int:order_id>")
def order_items(order_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/register")

    cur = mysql.connection.cursor()

    # проверка, что заказ принадлежит текущему пользователю
    cur.execute("SELECT user_id FROM orders WHERE id=%s", (order_id,))
    order = cur.fetchone()  # кортеж: (user_id,)
    if not order or order[0] != user_id:
        return redirect("/orders")

    # получаем товары
    cur.execute("""
        SELECT p.name, oi.price, oi.quantity
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        WHERE oi.order_id=%s
    """, (order_id,))
    rows = cur.fetchall()  # кортежи

    # преобразуем в список словарей
    items = [{"name": r[0], "price": float(r[1]), "quantity": r[2]} for r in rows]

    return render_template("order_items.html", items=items)


# =================== СОЗДАНИЕ ЗАКАЗА ===================
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

    cur = mysql.connection.cursor()

    cur.execute(
        "INSERT INTO addresses(user_id,country,city,street,postal_code) VALUES(%s,%s,%s,%s,%s)",
        (user_id, country, city, street, postal_code)
    )
    address_id = cur.lastrowid

    # подсчёт общей суммы
    total = 0
    for pid in cart:
        cur.execute("SELECT price FROM products WHERE id=%s", (pid,))
        product = cur.fetchone()
        if product:
            total += float(product[0])

    cur.execute(
        "INSERT INTO orders(user_id,total_price,status) VALUES(%s,%s,'new')",
        (user_id, total)
    )
    order_id = cur.lastrowid

    for pid in cart:
        cur.execute("SELECT price FROM products WHERE id=%s", (pid,))
        product = cur.fetchone()
        if product:
            cur.execute(
                "INSERT INTO order_items(order_id,product_id,quantity,price) VALUES(%s,%s,%s,%s)",
                (order_id, pid, 1, product[0])
            )

    mysql.connection.commit()
    session["cart"] = []

    return redirect("/orders")


# =================== СТРАНИЦА ОФОРМЛЕНИЯ ЗАКАЗА ===================
@orders.route("/checkout")
def checkout():
    user_id = session.get("user_id")
    cart = session.get("cart", [])

    if not user_id:
        return redirect("/register")
    if not cart:
        return redirect("/cart")

    cur = mysql.connection.cursor()

    cart_items = []
    total = 0

    for pid in cart:
        cur.execute("SELECT id,name,price,image FROM products WHERE id=%s", (pid,))
        product = cur.fetchone()
        if product:
            item = {
                "id": product[0],
                "name": product[1],
                "price": float(product[2]),
                "image": product[3],
                "quantity": 1
            }
            cart_items.append(item)
            total += item["price"]

    return render_template("checkout.html", cart_items=cart_items, total_price=total)