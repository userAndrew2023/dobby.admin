import psycopg2
from config import *

def connect():
    return psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)


def add_user(username, date, bot_id, user_id):
    with connect() as con:
        with con.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users_chats_ids WHERE username = {username}")
            print(cursor.fetchall())
            cursor.execute(f"INSERT INTO users (username, status, subscribe, bot_id, user_id) VALUES ('{username}', 'Active', '{date}', '{bot_id}', '{user_id}')")
        con.commit()


def deban(username):
    with connect() as con:
        with con.cursor() as cursor:
            cursor.execute(f"UPDATE users SET status = 'Active' WHERE username = '{username}'")
        con.commit()


def subscribe_last(date, username, bot_id):
    with connect() as con:
        with con.cursor() as cursor:
            cursor.execute(f"UPDATE users SET subscribe = '{date}' WHERE username = '{username}' AND bot_id = '{bot_id}'")
        con.commit()
