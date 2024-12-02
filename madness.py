import telebot
from telebot import types
import requests
import sqlite3
import time
import calendar
import datetime
from datetime import datetime as dt
import pytz
import traceback
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from config import *
from heroes import *

bot = telebot.TeleBot(token, threaded=False)
ua = UserAgent()

enemy_team = list()

connect = sqlite3.connect('users.db')  # создание дб
cursor = connect.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS all_messages(
    user_id INTEGER,
    nickname TEXT,
    activity_date TEXT,
    request TEXT,
    bot_answer TEXT,
    execution_time INTEGER
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER,
        nickname TEXT,
        messages INTEGER,
        first_activity TEXT,
        last_activity TEXT
    )""")
cursor.execute("""CREATE TABLE IF NOT EXISTS errors(
        user_id INTEGER,
        nickname TEXT,
        request TEXT,
        bot_answer TEXT,
        error TEXT
    )""")


def change_quantity_of_messages(message):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute(f"SELECT messages FROM users WHERE user_id = {message.chat.id}")
    messages = cur.fetchone()[0]
    messages += 1
    con.commit()
    cur.execute(f"UPDATE users SET messages = {messages} WHERE user_id = {message.chat.id}")
    con.commit()


def date(message):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute(f"SELECT first_activity FROM users WHERE user_id = {message.chat.id}")
    first_activity = cur.fetchone()[0].split()
    # Преобразую строку в объект datetime
    date_obj = dt.strptime(first_activity[0], '%Y-%m-%d')
    # Форматирую дату в словесный вид
    cur.execute(f"SELECT messages FROM users WHERE user_id = {message.chat.id}")
    messages = cur.fetchone()[0]
    months_rus = {
        1: 'января',
        2: 'февраля',
        3: 'марта',
        4: 'апреля',
        5: 'мая',
        6: 'июня',
        7: 'июля',
        8: 'августа',
        9: 'сентября',
        10: 'октября',
        11: 'ноября',
        12: 'декабря'
    }
    output_date = "{} {} {} года".format(date_obj.day, months_rus[date_obj.month], date_obj.year)
    con.commit()
    result = f"Вы впервые воспользовались ботом {output_date}. За всё время вы написали {messages} сообщений 💬."
    return result


@bot.message_handler(commands=['start', 'help', 'info', 'disadvantage', "allmes"])
def manual(message):
    start_time = time.time()
    bot_answer = None
    if message.text.lower() == '/start':
        bot_answer = "Привет, этот бот предназначен для помощи выбора лучших героев против пика противника, просто напишите героев вражеской команды. Вся статистика и информация постоянно обновляется с dotabuff. Не важно сколько героев ввести, бот выведет лучших персонажей против них.\n Пример:rubick, axe, pl, кристалка"
        bot.send_message(message.chat.id, bot_answer, reply_markup=userpanel())
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute(f'SELECT user_id from users')
        users_in_db = cur.fetchall()
        if (message.chat.id,) not in users_in_db:
            cur.execute("INSERT INTO users(user_id,nickname,messages,first_activity,last_activity)"
                        f"VALUES ({message.chat.id},\"{message.from_user.username}\",{0},\"{datetime.datetime.now(pytz.timezone('Europe/Moscow'))}\",\"{datetime.datetime.now(pytz.timezone('Europe/Moscow'))}\")")

            con.commit()
    elif message.text.lower() == '/help':
        bot_answer = "Этот бот предназначен для помощи выбора лучших героев против пика противника, просто напишите героев вражеской команды. Писать нужно без никакой команды, можно сокращениями, на русском, именами героев, любой регистр. Вся статистика и информация постоянно обновляется с dotabuff. Не важно сколько героев ввести, бот выведет лучших персонажей против них.\n Пример:rubick, axe, pl, кристалка\n\nТех. поддержка - @madness_nl"
        bot.send_message(message.chat.id, bot_answer, reply_markup=userpanel())
    elif message.text.lower() == '/info':
        bot_answer = "Этот бот предназначен для помощи выбора лучших героев против пика противника, просто напишите героев вражеской команды. Вся статистика и информация постоянно обновляется с dotabuff. Не важно сколько героев ввести, бот выведет лучших персонажей против них.\n Пример:rubick, axe, pl, кристалка"
        bot.send_message(message.chat.id, bot_answer, reply_markup=userpanel())
    elif message.text.lower() == '/disadvantage':
        bot_answer = 'Преимущество измеряется сравнением двух героев, независимым от их нормальной доли побед. Оно рассчитывается путем установления своей доли побед как "в", так и "за" пределами матча и сравнивая разницу с базовой долей побед.'
        bot.send_message(message.chat.id, bot_answer, reply_markup=userpanel())
    elif message.text.split()[0] == '/allmes' and message.chat.id == admin:
        try:
            # Установить соединение с базой данных
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()

            # Выбрать столбец user_id из таблицы users
            cursor.execute("SELECT user_id FROM users")

            # Извлечь результаты в виде списка
            user_ids = cursor.fetchall()

            # Закрыть соединение с базой данных
            cursor.close()
            connect.close()

            # Сделать цикл по элементам в списке user_ids
            mes = " ".join(message.text.split()[1:])
            for user_id in user_ids:
                bot.send_message(user_id[0], mes)
        except:
            pass


    end_time = time.time()
    execution_time = end_time - start_time
    database(message, bot_answer, execution_time)


    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute(
        f"UPDATE users SET last_activity = \"{datetime.datetime.now(pytz.timezone('Europe/Moscow'))}\" WHERE user_id = {message.chat.id}")
    con.commit()

    change_quantity_of_messages(message)

    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute(f"UPDATE users SET nickname = \"{message.from_user.username}\" WHERE user_id = {message.chat.id}")
    con.commit()

    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute(
        f"UPDATE users SET last_activity = \"{datetime.datetime.now(pytz.timezone('Europe/Moscow'))}\" WHERE user_id = {message.chat.id}")
    con.commit()



last_i = None  # для цикла ниже
pos_1 = dict()
pos_2 = dict()
pos_3 = dict()
pos_4 = dict()
pos_5 = dict()

result_pos_1 = list()
result_pos_2 = list()
result_pos_3 = list()
result_pos_4 = list()
result_pos_5 = list()


def restart():
    global allheroes, enemy_team, result_list, last_i, pos_1, pos_2, pos_3, pos_4, pos_5, result_pos_1, result_pos_2, result_pos_3, result_pos_4, result_pos_5
    allheroes = allheroes_reset.copy()
    enemy_team.clear()
    last_i = None
    pos_1.clear()
    pos_2.clear()
    pos_3.clear()
    pos_4.clear()
    pos_5.clear()
    result_pos_1.clear()
    result_pos_2.clear()
    result_pos_3.clear()
    result_pos_4.clear()
    result_pos_5.clear()


def database(message, bot_answer, execution_time):
    user_id = message.chat.id
    nickname = message.from_user.username
    request = message.text
    current_date_time = datetime.datetime.now().isoformat()
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute(
        "INSERT INTO all_messages(user_id, nickname, activity_date, request, bot_answer, execution_time) VALUES(?,?,?,?,?,?);",
        (user_id, nickname, current_date_time, request, bot_answer, execution_time))
    connect.commit()


@bot.message_handler(content_types=['text'])
def main(message):
    if message.text == b_2:
        bot.send_message(message.chat.id, date(message))
        change_quantity_of_messages(message)
    elif message.text == b_4:
        bot.send_message(message.chat.id, "Список героев 👇", reply_markup=b_1_inline)
        change_quantity_of_messages(message)
    elif message.text == b_3:
        r = requests.get("https://www.dotabuff.com/heroes/winning?date=week",
                         headers={
                             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'})  # ссылка + чтобы на дотабафф заходило
        soup = BeautifulSoup(r.content, "lxml")  # не трогай
        best_heroes = soup.find("tbody", class_="[&_tr:last-child]:tw-border-0").find_all("tr")
        best_winrate_heroes = list()
        for i in range(15):
            best_winrate_heroes.append(
                f"{best_heroes[i].find_all('td')[0].text.strip()} {best_heroes[i].find_all('td')[1].text.strip()}")
        best_winrate_heroes = '\n'.join(best_winrate_heroes)
        bot.send_message(message.chat.id, f"Герои с самым больши процентом побед за эту неделю 📊:\n\n{best_winrate_heroes}")

    elif message.text == b_5:
        bot_answer = "Этот бот предназначен для помощи выбора лучших героев против пика противника, просто напишите героев вражеской команды. Писать нужно без никакой команды, можно сокращениями, на русском, именами героев, любой регистр. Вся статистика и информация постоянно обновляется с dotabuff. Не важно сколько героев ввести, бот выведет лучших персонажей против них.\n Пример:rubick, axe, pl, кристалка\n\nТех. поддержка - @madness_nl"
        bot.send_message(message.chat.id, bot_answer, reply_markup=userpanel())
    else:
        try:
            start_time = time.time()
            restart()
            enemy_team = message.text.lower().split(",")
            enemy_team = set(enemy_team)
            try:
                enemy_team.remove(",")
            except:
                pass
            try:
                enemy_team.remove(".")
            except:
                pass
            try:
                enemy_team.remove("")
            except:
                pass
            enemy_team = list(enemy_team)
            print(enemy_team)
            for i in enemy_team:
                enemy_team[enemy_team.index(i)] = i.lstrip()
                i = i.lstrip()
                if i[-1] == "," or i[-1] == ".":
                    enemy_team[enemy_team.index(i)] = i[:-1]
                    i = i[:-1]
                hero_for_except = i
                for key, j in dota_heroes.items():
                    if i in j:
                        enemy_team[enemy_team.index(i)] = key
                        i = key
                        break
                print(i)
                r = requests.get('https://ru.dotabuff.com/heroes/' + i + '/counters',
                                 headers={
                                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'})  # ссылка + чтобы на дотабафф заходило
                soup = BeautifulSoup(r.content, "lxml")  # не трогай
                bad_hero = soup.find("table", class_="sortable").find("tbody").find_all("tr")
                for q in bad_hero:
                    disadvantage = q.find_all("td")[2].text.replace('%', "")  # превосходство + убираю % из значения
                    allheroes[q.find_all("td")[1].text.strip()] += float(
                        disadvantage)  # изменение превосходства в allheroes

            for i in enemy_team:  # удаление героев противника из allheroes
                r_2 = requests.get('https://ru.dotabuff.com/heroes/' + i,
                                   headers={
                                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'})
                soup_2 = BeautifulSoup(r_2.content, "lxml")
                hero = soup_2.find("div", class_="header-content-title").find("h1").find(
                    "small").previous_element.text.strip()
                del allheroes[hero]

            for i in allheroes.keys():  # округление чисел
                allheroes[i] = round(allheroes[i], 2)

            allheroes_sorted = sorted(allheroes.items(), key=lambda item: item[1],
                                      reverse=True)  # сортировка по значению
            for i, j in allheroes_sorted:
                if len(pos_1) == 10 and len(pos_2) == 10 and len(pos_3) == 10 and len(pos_4) == 10 and len(pos_5) == 10:
                    break
                if len(pos_1) < 10 and i in safelane:
                    pos_1[i] = j
                if len(pos_2) < 10 and i in midlane:
                    pos_2[i] = j
                if len(pos_3) < 10 and i in offlane:
                    pos_3[i] = j
                if len(pos_4) < 10 and i in hard_support:
                    pos_4[i] = j
                if len(pos_5) < 10 and i in safe_support:
                    pos_5[i] = j

            result = f'Лучшие герои против {", ".join(sorted(enemy_team))}: \n\nЛучшие керри (pos 1): \n'
            for i, j in pos_1.items():
                result_dotabuff = i + " : " + str(j)
                result_pos_1.append(result_dotabuff)
            result += "\n".join(result_pos_1)
            result += "\n\nЛучшие мидеры (pos 2): \n"
            for i, j in pos_2.items():
                result_dotabuff = i + " : " + str(j)
                result_pos_2.append(result_dotabuff)
            result += "\n".join(result_pos_2)
            result += "\n\nЛучшие оффлейнеры (pos 3): \n"
            for i, j in pos_3.items():
                result_dotabuff = i + " : " + str(j)
                result_pos_3.append(result_dotabuff)
            result += "\n".join(result_pos_3)
            result += "\n\nЛучшие хард сапорты (pos 4): \n"
            for i, j in pos_4.items():
                result_dotabuff = i + " : " + str(j)
                result_pos_4.append(result_dotabuff)
            result += "\n".join(result_pos_4)
            result += "\n\nЛучшие герои полной поддержки (pos 5): \n"
            for i, j in pos_5.items():
                result_dotabuff = i + " : " + str(j)
                result_pos_5.append(result_dotabuff)
            result += "\n".join(result_pos_5)
            bot_answer = result
            bot.send_message(message.chat.id, bot_answer, reply_markup=userpanel())  # вывод
        except:
            restart()
            bot_answer = f"Ошибка! Проверьте написание героев. Пишите героев через запятую. /help\nПример:rubick, axe, pl, кристалка\n\nОшибка в слове: {hero_for_except}"
            bot.reply_to(message, bot_answer, reply_markup=b_1_inline)

            con = sqlite3.connect("users.db")
            cur = con.cursor()

            user_id = message.chat.id
            nickname = message.from_user.username
            request = message.text.lower()
            error = traceback.format_exc()

            cur.execute("INSERT INTO errors(user_id,nickname,request,bot_answer,error) VALUES(?,?,?,?,?);",
                        (user_id, nickname, request, bot_answer, error))

            con.commit()

        end_time = time.time()
        execution_time = end_time - start_time
        database(message, bot_answer, execution_time)

        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute(
            f"UPDATE users SET last_activity = \"{datetime.datetime.now(pytz.timezone('Europe/Moscow'))}\" WHERE user_id = {message.chat.id}")
        con.commit()

        change_quantity_of_messages(message)

        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute(f"UPDATE users SET nickname = \"{message.from_user.username}\" WHERE user_id = {message.chat.id}")
        con.commit()


bot.polling(none_stop=True)
