from flask import Blueprint, render_template, request, redirect, session
from db import mysql
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    print("LOGIN ROUTE CALLED")
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            error = "Введите email и пароль"
        else:
            cur = mysql.connection.cursor()
            cur.execute(
                "SELECT id, name, email, password_hash, role FROM users WHERE email=%s",
                (email,)
            )
            user = cur.fetchone()
            cur.close()

            if not user:
                error = "Неверный email или пароль"
            else:
                stored_password = user[3] or ""
                if stored_password.startswith(("pbkdf2:sha256:", "scrypt:")):
                    valid = check_password_hash(stored_password, password)
                else:
                    valid = stored_password == password

                if valid:
                    session["user_id"] = user[0]
                    session["role"] = user[4]
                    if user[4] == "admin":
                        return redirect("/admin")
                    return redirect("/profile")
                else:
                    error = "Неверный email или пароль"

    return render_template("login.html", error=error)

@auth.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            error = "Введите email и пароль"
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, password_hash, role FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
            cur.close()

            if not user or user[2] != "admin":
                error = "Нет доступа"
            else:
                stored_password = user[1] or ""
                if stored_password.startswith(("pbkdf2:sha256:", "scrypt:")):
                    valid = check_password_hash(stored_password, password)
                else:
                    valid = stored_password == password

                if valid:
                    session["user_id"] = user[0]
                    session["role"] = "admin"
                    return redirect("/admin")
                else:
                    error = "Нет доступа"

    return render_template("admin_login.html", error=error)


# ------------------- Регистрация -------------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            error = "Заполните все поля"
        else:
            hashed_password = generate_password_hash(password)

            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users WHERE email=%s", (email,))
            existing_user = cur.fetchone()

            if existing_user:
                cur.close()
                error = "Пользователь уже существует"
            else:
                cur.execute(
                    "INSERT INTO users(name,email,password_hash,role) VALUES(%s,%s,%s,'user')",
                    (name, email, hashed_password)
                )
                mysql.connection.commit()
                cur.close()
                return redirect("/login")

    return render_template("register.html", error=error)


# ------------------- Профиль -------------------
@auth.route("/profile")
def profile():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    cur = mysql.connection.cursor()
    cur.execute("SELECT name, email FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return redirect("/login")

    user_data = {
        "fullname": user[0],
        "email": user[1],
        "avatar": "img/default_avatar.jpg",
        "username": user[0]
    }

    return render_template("profile.html", user=user_data)


# ------------------- Выход -------------------
@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("role", None)
    return redirect("/")