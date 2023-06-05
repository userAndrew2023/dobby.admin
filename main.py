import psycopg2
import pymysql as pymysql
import requests
from telebot import TeleBot, types

import db_working
from config import *

bot = TeleBot(token=TOKEN)
temp_bots = {}
allowed_users = ['msnetwin', 'aircradmin']


class AddUser:
    def __init__(self):
        self.username = None
        self.date = None


def connect():
    return psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)


def main_bar(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    con = connect()
    with con.cursor() as cursor:
        cursor.execute("SELECT * FROM bots")
        for i in cursor.fetchall():
            markup.add(types.InlineKeyboardButton(i[1], callback_data=f"bots:{i[1]}"))
    con.close()
    bot.send_message(message.chat.id, "Добро пожаловать, выберите бота, чтобы продолжить", reply_markup=markup)
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "😉", reply_markup=markup)


@bot.message_handler(commands=["start"])
def start(message: types.Message):
    if message.from_user.username not in allowed_users:
        return
    main_bar(message)


@bot.callback_query_handler(lambda callback: callback.data.startswith("bots:"))
def bot_actions(call: types.CallbackQuery):
    if call.from_user.username not in allowed_users:
        return
    data = call.data.split(":")[-1]
    temp_bots[call.from_user.id] = data
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [
        types.KeyboardButton("Юзеры"),
        types.KeyboardButton("Главное меню")
    ]
    markup.add(*items, row_width=2)
    bot.send_message(call.from_user.id, "Выберите действие для бота", reply_markup=markup)


@bot.callback_query_handler(lambda callback: callback.data.startswith("ban:"))
def bot_actions(call: types.CallbackQuery):
    if call.from_user.username not in allowed_users:
        return
    data = call.data.split(":")[-1]
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(f"SELECT * FROM users WHERE (username = '{data}');")
        cursor.execute(f"UPDATE users SET status = 'Ban' WHERE (username = '{data}');")
    con.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [
        types.KeyboardButton("Юзеры"),
        types.KeyboardButton("Главное меню")
    ]
    markup.add(*items, row_width=1)
    bot.send_message(call.from_user.id, "Пользователь забанен.",
                     reply_markup=markup)
    con.close()


@bot.callback_query_handler(lambda callback: callback.data.startswith("deban:"))
def bot_actions(call: types.CallbackQuery):
    if call.from_user.username not in allowed_users:
        return
    db_working.deban(call.data.split(":")[1])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [
        types.KeyboardButton("Юзеры"),
        types.KeyboardButton("Главное меню")
    ]
    markup.add(*items, row_width=1)
    bot.send_message(call.from_user.id, "Пользователь разблокирован.",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Главное меню")
def main_menu(message: types.Message):
    if message.from_user.username not in allowed_users:
        return
    main_bar(message)


@bot.message_handler(func=lambda message: message.text == "Юзеры")
def stats(message: types.Message):
    if message.from_user.username not in allowed_users:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[
        types.KeyboardButton("Активные"),
        types.KeyboardButton("Неактивные"),
        types.KeyboardButton("Добавить Юзера"),
        types.KeyboardButton("Статистика"),
        types.KeyboardButton("Главное меню")
    ], row_width=2)
    bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)
    con.close()


@bot.message_handler(func=lambda message: message.text == "Добавить Юзера")
def stats(message: types.Message):
    bot.send_message(message.chat.id, "Введите username Юзера", reply_markup=types.ReplyKeyboardRemove())
    users[message.chat.id] = "ADD USER"


@bot.message_handler(func=lambda message: message.text == "Статистика")
def stats(message: types.Message):
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM users WHERE bot_id = '{temp_bots.get(message.chat.id, False)}'")
        f = cursor.fetchall()
        if len(f) == 0:
            bot.send_message(message.chat.id, "Пользователи отсутствуют")
        for i in f:
            markup = types.InlineKeyboardMarkup()
            if temp_bots.get(message.chat.id) != "Dobby.Seller":
                bot.send_message(message.chat.id, f"<b>Юзер</b>: @{i[1]}\n"
                                                  f"<b>Подписка до</b>: {i[3]}",
                                 reply_markup=markup, parse_mode="HTML")
            else:
                conq = pymysql.connect(host="localhost", user="root", password="1234", db="dobby.admin")
                with conq.cursor() as cursor4:
                    cursor4.execute(f"SELECT * FROM `client_bots` WHERE user_id = '{i[-1]}'")
                    print(i[-1])
                    token = cursor4.fetchall()[0][1]
                conq.close()

                url = f"https://api.telegram.org/bot{token}/getMe"
                headers = {
                    "accept": "application/json",
                    "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)"
                }
                try:
                    username = "@" + requests.post(url, headers=headers).json()['result']['username']
                except:
                    username = "Отсутствует"
                bot.send_message(message.chat.id, f"<b>Юзер</b>: @{i[1]}\n"
                                                  f"<b>Подписка до</b>: {i[3]}\n"
                                                  f"<b>Клиентский бот</b>: {username}",
                                 reply_markup=markup, parse_mode="HTML")
    con.close()


@bot.message_handler(func=lambda message: users.get(message.chat.id) == "ADD USER")
def stats(message: types.Message):
    bot.send_message(message.chat.id, "Введите дату окончания подписки в формате дд.мм.гггг")
    temp_users[message.chat.id] = message.text
    users[message.chat.id] = "DATE ADD USER"


@bot.message_handler(func=lambda message: users.get(message.chat.id) == "DATE ADD USER")
def stats(message: types.Message):
    db_working.add_user(username=temp_users.get(message.chat.id), date=message.text,
                        bot_id=temp_bots.get(message.chat.id), user_id=message.chat.id)
    users[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Главное меню")
    markup.add("Юзеры")
    bot.send_message(message.chat.id, "Вы успешно добавили пользователя", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Активные")
def stats(message: types.Message):
    if message.from_user.username not in allowed_users:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[
        types.KeyboardButton("Главное меню"),
        types.KeyboardButton("Юзеры")
    ], row_width=2)
    con = connect()
    with con.cursor() as cursor:
        users = {}
        cursor.execute(
            f"SELECT * FROM users WHERE bot_id = '{temp_bots.get(message.chat.id, False)}' AND status = 'Active'")
        f = cursor.fetchall()
        if len(f) == 0:
            bot.send_message(message.chat.id, "Активных пользователей нет", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)
        for i in f:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Забанить", callback_data=f"ban:{i[1]}"))
            bot.send_message(message.chat.id, f"<b>Юзер</b>: @{i[1]}\n"
                                              f"<b>Подписка до</b>: {i[3]}",
                             reply_markup=markup, parse_mode="HTML")
    con.close()


@bot.message_handler(func=lambda message: message.text == "Неактивные")
def stats(message: types.Message):
    if message.from_user.username not in allowed_users:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[
        types.KeyboardButton("Главное меню"),
        types.KeyboardButton("Юзеры")
    ], row_width=2)
    con = connect()
    with con.cursor() as cursor:
        users = {}
        cursor.execute(
            f"SELECT * FROM users WHERE bot_id = '{temp_bots.get(message.chat.id, False)}' AND status = 'Ban'")
        f = cursor.fetchall()
        if len(f) == 0:
            bot.send_message(message.chat.id, "Неактивных пользователей нет", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)
        for i in f:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Разбанить", callback_data=f"deban:{i[1]}"))
            bot.send_message(message.chat.id, f"<b>Юзер</b>: @{i[1]}\n"
                                              f"<b>Подписка до</b>: {i[3]}",
                             reply_markup=markup, parse_mode="HTML")
    con.close()


if __name__ == "__main__":
    users = {}
    temp_users = {}
    con = connect()
    with con.cursor() as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                      id SERIAL NOT NULL,
                      username text NOT NULL,
                      status text NOT NULL,
                      subscribe text NOT NULL,
                      bot_id text NOT NULL,
                      user_id text NOT NULL,
                      PRIMARY KEY (id));""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                      id SERIAL NOT NULL,
                      bot_id text NOT NULL,
                      username text NOT NULL,
                      text text NOT NULL,
                      datetime text NOT NULL,
                      PRIMARY KEY (id));""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS bots (
                      id SERIAL NOT NULL,
                      name text NOT NULL,
                      img text NOT NULL,
                      messages text NOT NULL,
                      status text NOT NULL,
                      PRIMARY KEY (id));""")
    con.commit()
    con.close()
    bot.infinity_polling()
