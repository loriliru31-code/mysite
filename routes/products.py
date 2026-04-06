from flask import Blueprint, render_template, request, jsonify
from db import mysql

products = Blueprint("products", __name__)

# ---------------- Главная страница с популярными товарами ----------------
@products.route("/")
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, sku, name, description, price, category_id, image FROM products LIMIT 4")
    products_list = cur.fetchall()
    cur.close()

    # Преобразуем кортежи в словари
    products_list = [
        {
            "id": p[0],
            "sku": p[1],
            "name": p[2],
            "description": p[3],
            "price": float(p[4]),
            "category_id": p[5],
            "image": p[6] or "img/default_product.jpg"
        }
        for p in products_list
    ]

    return render_template("index.html", products=products_list)

# ---------------- Страница каталога ----------------
@products.route("/catalog")
def catalog():
    cur = mysql.connection.cursor()

    cur.execute("SELECT id, name FROM categories")
    categories = cur.fetchall()

    cur.execute("""
        SELECT id, sku, name, description, price, category_id, image
        FROM products
        LIMIT 20
    """)
    products_list = cur.fetchall()
    cur.close()

    products_list = [
        {
            "id": p[0],
            "sku": p[1],
            "name": p[2],
            "description": p[3],
            "price": float(p[4]),
            "category_id": p[5],
            "image": p[6] or "img/default_product.jpg"
        }
        for p in products_list
    ]

    return render_template(
        "catalog.html",
        products=products_list,
        categories=categories
    )

# ---------------- API получения характеристик категории ----------------
@products.route("/api/attributes/<int:category_id>")
def get_attributes(category_id):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT a.id, a.name
        FROM attributes a
        JOIN category_attributes ca ON a.id = ca.attribute_id
        WHERE ca.category_id = %s
    """, (category_id,))

    attributes = cur.fetchall()
    data = []

    for attr in attributes:
        cur.execute("""
            SELECT DISTINCT value
            FROM product_attribute_values
            WHERE attribute_id = %s
        """, (attr[0],))
        values = cur.fetchall()
        data.append({
            "id": attr[0],
            "name": attr[1],
            "values": [v[0] for v in values]
        })

    cur.close()
    return jsonify(data)

# ---------------- API фильтрации товаров ----------------
@products.route("/api/filter_products", methods=["POST"])
def filter_products():
    data = request.json
    category_id = data.get("category_id")
    filters = data.get("filters", {})

    cur = mysql.connection.cursor()
    query = """
    SELECT DISTINCT id, sku, name, description, price, category_id, image
    FROM products
"""
    params = []

    if category_id:
        query += " WHERE category_id = %s"
        params.append(category_id)

    for attr_id, value in filters.items():
        query += """
            AND id IN (
                SELECT product_id
                FROM product_attribute_values
                WHERE attribute_id = %s AND value = %s
            )
        """
        params.append(attr_id)
        params.append(value)

    cur.execute(query, tuple(params))

    result = []
    for p in cur.fetchall():
        result.append({
            "id": p[0],
            "sku": p[1],
            "name": p[2],
            "description": p[3],
            "price": float(p[4]),
            "category_id": p[5],
            "image": p[6] or "img/default_product.jpg"
        })

    cur.close()
    return jsonify(result)

@products.route("/product/<sku>")
def product_page(sku):
    cursor = mysql.connection.cursor()

    # Основная информация о товаре
    cursor.execute("""
        SELECT id, sku, name, description, price, category_id, image
        FROM products
        WHERE sku = %s
    """, (sku,))
    
    p = cursor.fetchone()

    if not p:
        cursor.close()
        return "Товар не найден", 404

    product = {
        "id": p[0],
        "sku": p[1],
        "name": p[2],
        "description": p[3],
        "price": float(p[4]),
        "category_id": p[5],
        "image": p[6] or "img/default_product.jpg"
    }

    # характеристики
    cursor.execute("""
        SELECT a.name, pav.value
        FROM product_attribute_values pav
        JOIN attributes a ON pav.attribute_id = a.id
        WHERE pav.product_id = %s
    """, (product["id"],))

    specs = cursor.fetchall()
    product["specs"] = [{"name": s[0], "value": s[1]} for s in specs]

    cursor.close()

    return render_template("product.html", product=product)