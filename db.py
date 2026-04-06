import pymysql
from flask import g
from config import *

# Функция для получения подключения к базе
def get_db():
    if "db" not in g:
        g.db = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor  # возвращает словари вместо кортежей
        )
    return g.db

# Функция для закрытия соединения после запроса
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
