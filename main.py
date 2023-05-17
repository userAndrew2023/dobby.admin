import datetime
import psycopg2
from telebot import TeleBot, types
from config import *

bot = TeleBot(token=TOKEN)
temp_bots = {}
allowed_users = ['msnetwin', 'aircradmin']


def connect():
    return psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)


def main_bar(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    con = connect()
    with con.cursor() as cursor:
        cursor.execute("SELECT * FROM bots")
        for i in cursor.fetchall():
            markup.add(types.InlineKeyboardButton(i[1], callback_data=f"bots:{i[0]}"))
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
    if message.from_user.username not in allowed_users:
        return
    data = call.data.split(":")[-1]
    temp_bots[call.from_user.id] = data
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [
        types.KeyboardButton("Получить сообщения"),
        types.KeyboardButton("Сообщения за сегодня"),
        types.KeyboardButton("Статистика"),
        types.KeyboardButton("Юзеры"),
        types.KeyboardButton("Главное меню")
    ]
    markup.add(*items, row_width=2)
    bot.send_message(call.from_user.id, "Выберите действие для бота", reply_markup=markup)


@bot.callback_query_handler(lambda callback: callback.data.startswith("messages:"))
def bot_actions(call: types.CallbackQuery):
    if call.from_user.username not in allowed_users:
        return
    data = call.data.split(":")[-1]
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(f"SELECT * FROM messages WHERE (id = '{data}');")
        username = cursor.fetchall()[0][2]
        cursor.execute(f"UPDATE users SET status = 'Ban' WHERE (username = '{username}');")
    con.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [
        types.KeyboardButton("Главное меню")
    ]
    markup.add(*items, row_width=1)
    bot.send_message(call.from_user.id, "Пользователь забанен. Теперь его сообщения не будут появляться здесь",
                     reply_markup=markup)


@bot.callback_query_handler(lambda callback: callback.data.startswith("users:"))
def bot_actions(call: types.CallbackQuery):
    if call.from_user.username not in allowed_users:
        return
    data = call.data.split(":")[-1]
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(f"UPDATE users SET status = 'Ban' WHERE (username = '{data}');")
    con.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = [
        types.KeyboardButton("Главное меню")
    ]
    markup.add(*items, row_width=1)
    bot.send_message(call.from_user.id, "Пользователь забанен. Теперь его сообщения не будут появляться здесь",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Главное меню")
def main_menu(message: types.Message):
    if message.from_user.username not in allowed_users:
        return
    main_bar(message)


@bot.message_handler(func=lambda message: message.text == "Получить сообщения")
def main_menu(message: types.Message):
    if message.from_user.username not in allowed_users:
        return
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(f"SELECT * FROM messages WHERE bot_id = '{temp_bots.get(message.chat.id, False)}'")
        fetch = cursor.fetchall()
        for i in fetch:
            cursor.execute(f"SELECT * FROM users WHERE username = '{i[2]}'")
            if cursor.fetchall()[0][-1] != "Banned":
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Забанить", callback_data=f"messages:{i[0]}"))
                bot.send_message(message.chat.id, f"<b>Ник отправителя</b>: @{i[2]}\n"
                                                  f"<b>Сообщение</b>: {i[3]}\n"
                                                  f"<b>Дата</b>: {i[4]}",
                                 reply_markup=markup, parse_mode="HTML")
    con.close()


@bot.message_handler(func=lambda message: message.text == "Сообщения за сегодня")
def main_menu(message: types.Message):
    if message.from_user.username not in allowed_users:
        return
    date = datetime.datetime.now()
    datef = f"{date.day}.{date.month}.{date.year}"
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(f"SELECT * FROM messages WHERE bot_id = '{temp_bots.get(message.chat.id, False)}'"
                       f" AND datetime = '{datef}'")
        fetch = cursor.fetchall()
        for i in fetch:
            cursor.execute(f"SELECT * FROM users WHERE username = '{i[2]}'")
            if cursor.fetchall()[0][-1] != "Banned":
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Забанить", callback_data=f"messages:{i[0]}"))
                bot.send_message(message.chat.id, f"<b>Ник отправителя</b>: @{i[2]}\n"
                                                  f"<b>Сообщение</b>: {i[3]}\n",
                                 reply_markup=markup, parse_mode="HTML")
    con.close()


@bot.message_handler(func=lambda message: message.text == "Статистика")
def stats(message: types.Message):
    if message.from_user.username not in allowed_users:
        return
    con = connect()
    with con.cursor() as cursor:
        cursor.execute(f"SELECT * FROM messages WHERE bot_id = '{temp_bots.get(message.chat.id, False)}'")
        len1 = len(cursor.fetchall())
    with con.cursor() as cursor:
        date = datetime.datetime.now()
        datef = f"{date.day}.{date.month}.{date.year}"
        cursor.execute(f"SELECT * FROM messages WHERE bot_id = '{temp_bots.get(message.chat.id, False)}'"
                       f" AND datetime = '{datef}'")
        len2 = len(cursor.fetchall())
    with con.cursor() as cursor:
        users = []
        cursor.execute(f"SELECT * FROM messages WHERE bot_id = '{temp_bots.get(message.chat.id, False)}'")
        for i in cursor.fetchall():
            if i[2] not in users:
                users.append(i[2])
        len3 = len(users)
    bot.send_message(message.chat.id, f"<b>Всего сообщений</b>: {len1}\n"
                                      f"<b>Сообщений сегодня</b>: {len2}\n"
                                      f"<b>Юзеров всего</b>: {len3}\n", parse_mode="HTML")
    con.close()


@bot.message_handler(func=lambda message: message.text == "Юзеры")
def stats(message: types.Message):
    if message.from_user.username not in allowed_users:
        return
    con = connect()
    with con.cursor() as cursor:
        users = {}
        cursor.execute(f"SELECT * FROM messages WHERE bot_id = '{temp_bots.get(message.chat.id, False)}'")
        for i in cursor.fetchall():
            if i[2] not in users.keys():
                users[i[2]] = 1
            else:
                users[i[2]] += 1
        for key, value in users.items():
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Забанить", callback_data=f"users:{key}"))
            bot.send_message(message.chat.id, f"<b>Юзер</b>: @{key}\n"
                                              f"<b>Сообщений в этом боте</b>: {value}",
                             reply_markup=markup, parse_mode="HTML")


if __name__ == "__main__":
    con = connect()
    with con.cursor() as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                      id SERIAL NOT NULL,
                      username text NOT NULL,
                      status text NOT NULL,
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
