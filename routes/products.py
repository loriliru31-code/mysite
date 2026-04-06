from flask import Blueprint, render_template, request, jsonify
from db import get_db

products = Blueprint("products", __name__)

@products.route("/")
def index():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, sku, name, description, price, category_id, image FROM products LIMIT 4")
        products_list = cur.fetchall()

    products_list = [
        {
            "id": p["id"],
            "sku": p["sku"],
            "name": p["name"],
            "description": p["description"],
            "price": float(p["price"]),
            "category_id": p["category_id"],
            "image": p["image"] or "img/default_product.jpg"
        } for p in products_list
    ]

    return render_template("index.html", products=products_list)

@products.route("/catalog")
def catalog():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, name FROM categories")
        categories = cur.fetchall()

        cur.execute("SELECT id, sku, name, description, price, category_id, image FROM products LIMIT 20")
        products_list = cur.fetchall()

    products_list = [
        {
            "id": p["id"],
            "sku": p["sku"],
            "name": p["name"],
            "description": p["description"],
            "price": float(p["price"]),
            "category_id": p["category_id"],
            "image": p["image"] or "img/default_product.jpg"
        } for p in products_list
    ]

    return render_template("catalog.html", products=products_list, categories=categories)

@products.route("/api/attributes/<int:category_id>")
def get_attributes(category_id):
    db = get_db()
    data = []
    with db.cursor() as cur:
        cur.execute("SELECT a.id, a.name FROM attributes a JOIN category_attributes ca ON a.id = ca.attribute_id WHERE ca.category_id=%s", (category_id,))
        attributes = cur.fetchall()
        for attr in attributes:
            cur.execute("SELECT DISTINCT value FROM product_attribute_values WHERE attribute_id=%s", (attr["id"],))
            values = cur.fetchall()
            data.append({
                "id": attr["id"],
                "name": attr["name"],
                "values": [v["value"] for v in values]
            })
    return jsonify(data)

@products.route("/api/filter_products", methods=["POST"])
def filter_products():
    data = request.json
    category_id = data.get("category_id")
    filters = data.get("filters", {})

    db = get_db()
    with db.cursor() as cur:
        query = "SELECT DISTINCT id, sku, name, description, price, category_id, image FROM products"
        params = []

        if category_id:
            query += " WHERE category_id=%s"
            params.append(category_id)

        for attr_id, value in filters.items():
            query += " AND id IN (SELECT product_id FROM product_attribute_values WHERE attribute_id=%s AND value=%s)"
            params.extend([attr_id, value])

        cur.execute(query, tuple(params))
        result = cur.fetchall()

    result = [
        {
            "id": p["id"],
            "sku": p["sku"],
            "name": p["name"],
            "description": p["description"],
            "price": float(p["price"]),
            "category_id": p["category_id"],
            "image": p["image"] or "img/default_product.jpg"
        } for p in result
    ]

    return jsonify(result)

@products.route("/product/<sku>")
def product_page(sku):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, sku, name, description, price, category_id, image FROM products WHERE sku=%s", (sku,))
        p = cur.fetchone()
        if not p:
            return "Товар не найден", 404

        product = {
            "id": p["id"],
            "sku": p["sku"],
            "name": p["name"],
            "description": p["description"],
            "price": float(p["price"]),
            "category_id": p["category_id"],
            "image": p["image"] or "img/default_product.jpg"
        }

        cur.execute("SELECT a.name, pav.value FROM product_attribute_values pav JOIN attributes a ON pav.attribute_id = a.id WHERE pav.product_id=%s", (product["id"],))
        specs = cur.fetchall()
        product["specs"] = [{"name": s["name"], "value": s["value"]} for s in specs]

    return render_template("product.html", product=product)
