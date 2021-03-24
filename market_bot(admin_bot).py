import telebot
import pymysql
import datetime


# ТОКЕН АДМИН БОТА
token = '1328042742:AAEC2xigidS52g74PGuJ6zHxWRJzOZpsWQ8'
bot = telebot.TeleBot(token)


# ТОКЕН ОСНОВНОГО БОТА
main_token = '1024091588:AAFYiRd5sm5z4Ol2aF1lxFqayR8o1XNxIo0'
main_bot = telebot.TeleBot(main_token)
server_ip = 'localhost'
login = "telegrambotadmin"
password = "botparol00115566"
step = 0
errors_array = []
sql = {}
chat_id = {}
block_status = 'Заблокировать'


bot_db = pymysql.connect(host=server_ip,
                         user=login,
                         password=password,
                         db='market_bot',
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)
cursor = bot_db.cursor()
main_menu = telebot.types.ReplyKeyboardMarkup(True)
main_menu.add('Отправить сообщение всем пользователям')\
         .add('Посмотерть инвентарь пользователя')\
         .add('Список всех пользователей')


user_menu = telebot.types.ReplyKeyboardMarkup(True)
user_menu.add('Изменить сумму на счету')\
         .add('Изменить энергию')\
         .add('Последнее сообщение пользователя')\
         .add('Посмотреть рефералов пользователя')\
         .add('%s пользователя' % block_status)\
         .add('В главное меню')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Главное меню',
                     reply_markup=main_menu)


@bot.message_handler(content_types=['text'])
def send_text(message):
    global step
    global sql
    step_func = {1: send_all,
                 2: read_ref_code,
                 3: look_inventory,
                 11: change_money,
                 22: change_energy}
    functions = {'Отправить сообщение всем пользователям': mess,
                 'Посмотреть рефералов пользователя': ref,
                 'Посмотерть инвентарь пользователя': read_inv_code,
                 'Список всех пользователей': all_user,
                 'Изменить сумму на счету': read_money,
                 'Изменить энергию': read_energy,
                 'Последнее сообщение пользователя': last_message,
                 'Заблокировать пользователя': block,
                 'Разблокировать пользователя': block,
                 'В главное меню': back_to_mm}
    try:
        if message.text in functions:
            step = functions[message.text](message=message)
        elif step in step_func:
            step = step_func[step](message=message)
    except KeyError:
        bot.send_message(0,
                         'Я тебя не совсем понял 🙃 \nНажми нужную кнопку меню.')


def mess(message):
    bot.send_message(message.chat.id,
                     'Введите сообщение')
    return 1


def all_user(message):
    global sql
    sql[message.chat.id] = 'SELECT chat_id,user_name FROM users;'
    data = sql_func(message)
    text = ''
    bot.send_message(message.chat.id,
                     'All users')
    k = 0
    for i in data:
        text += '#id%s %s\n' % (i['chat_id'], i['user_name'])
        k += 1
        if k >= 10:
            bot.send_message(message.chat.id,
                             text)
            text = ''
            k = 0
    if k < 10:
        bot.send_message(message.chat.id,
                         text)


def send_all(message):
    global sql
    sql[message.chat.id] = "SELECT chat_id FROM users"
    data = sql_func(message)
    for i in data:
        main_bot.send_message(i['chat_id'],
                              message.text)
    return 10


def ref(message):
    bot.send_message(message.chat.id,
                     'Введите chat_id пользователя ,его можно увидеть в его реферальноый ссылке он идет после ?start=')
    return 2


def read_ref_code(message):
    global sql
    sql[message.chat.id] = "SELECT user_name FROM users WHERE ref_id=%s" % message.text
    data = sql_func(message)
    if data == ():
        bot.send_message(message.chat.id,
                         'У пользователя нет рефералов')
    else:
        for i in data:
            bot.send_message(message.chat.id,
                             i['user_name'])
    return 20


def read_inv_code(message):
    bot.send_message(message.chat.id,
                     'Введите chat_id пользователя ,его можно увидеть в его реферальноый ссылке он идет после ?start=')
    return 3


def look_inventory(message):
    global sql
    global chat_id
    global block_status
    if str(message.text).isdigit() == False:
        bot.send_message(message.chat.id,
                         'Введите id',
                         reply_markup=main_menu)
        return 3
    chat_id[message.chat.id] = message.text
    sql[message.chat.id] = 'SELECT user_id FROM users WHERE chat_id=%s' % chat_id[message.chat.id]
    data = sql_func(message)
    if data == ():
        bot.send_message(message.chat.id,
                         'Пользователь не найдет',
                         reply_markup=main_menu)
        return 3
    sql[message.chat.id] = "SELECT * FROM users where chat_id='%s'" % message.text
    data = sql_func(message)
    bot.send_message(message.chat.id,
                     'Денег на счету = %s. Энергия = %s' % (data[0]['user_money'],
                                                            data[0]['energy']))
    sql[message.chat.id] = "select * from inventory where user_id='%s'" % message.text
    data = sql_func(message)
    if data == ():
        bot.send_message(message.chat.id,
                         'Нет предметов в инвентаре')
    else:
        types = {'🦺Броня🦺': armour_out,
                 '🏹Оружие🏹': weapon_out,
                 '🥾Сапоги🥾': boots_out,
                 '🧤Перчатки🧤': gloves_out,
                 '👖Штаны👖': pants_out}
        text_array = []
        k = 0
        output = ''
        for i in data:
            text = types[i['item_type']](i=i)
            text_array.append(text)
        for i in range(len(data)):
            if data[i]['on_user'] == 0:
                output += 'Снято : %s \n\n' % text_array[i]
            else:
                output += 'Надето : %s \n\n' % text_array[i]
            k += 1
            if k == 10:
                bot.send_message(message.chat.id,
                                 output)
                output = ''
                k = 0
        if k < 10:
            bot.send_message(message.chat.id,
                             output)
    bot.send_message(message.chat.id,
                     'Меню пользователя',
                     reply_markup=user_menu)
    return 10


def armour_out(i):
    market_status = 'Не продаеться'
    if i['on_market'] == 1:
        market_status = 'На продаже'
    text = "%s  '%s'  Защита🦺(%s) | %s (%s)" % (i['item_name'], i['item_type'],  i['item_power'], i['buy_code'], market_status)
    return text


def weapon_out(i):
    market_status = 'Не продаеться'
    if i['on_market'] == 1:
        market_status = 'На продаже'
    text = "%s  '%s'  Урон🏹(%s) | %s (%s)" % (i['item_name'], i['item_type'],  i['item_power'], i['buy_code'], market_status)
    return text


def boots_out(i):
    market_status = 'Не продаеться'
    if i['on_market'] == 1:
        market_status = 'На продаже'
    text = "%s  '%s'  Бонус к скорости🥾(%s) | %s (%s)" % (i['item_name'], i['item_type'],  i['item_power'], i['buy_code'], market_status)
    return text


def gloves_out(i):
    market_status = 'Не продаеться'
    if i['on_market'] == 1:
        market_status = 'На продаже'
    text = "%s  '%s'  Бонус к энергии⚡(%s) | %s (%s)" % (i['item_name'], i['item_type'],  i['item_power'], i['buy_code'], market_status)
    return text


def pants_out(i):
    market_status = 'Не продаеться'
    if i['on_market'] == 1:
        market_status = 'На продаже'
    text = "%s  '%s'  Бонус к ОЗ💚(%s) | %s (%s)" % (i['item_name'], i['item_type'],  i['item_power'], i['buy_code'], market_status)
    return text


def read_money(message):
    bot.send_message(message.chat.id,
                     'Введите новую сумму')
    return 11


def change_money(message):
    global sql
    global chat_id
    if str(message.text).isdigit() == False:
        bot.send_message(message.chat.id,
                         'Введите число')
        return 11
    sql[message.chat.id] = "UPDATE users SET user_money=%s WHERE chat_id='%s'" % (message.text, chat_id[message.chat.id])
    bot.send_message(message.chat.id,
                     'ok')
    sql_func(message)


def read_energy(message):
    bot.send_message(message.chat.id,
                     'Введите новое количество энергии')
    return 22


def change_energy(message):
    global sql
    global chat_id
    if str(message.text).isdigit() == False:
        bot.send_message(message.chat.id,
                         'Введите число')
        return 22
    sql[message.chat.id] = "UPDATE users SET energy=%s WHERE chat_id=%s" % (message.text, chat_id[message.chat.id])
    bot.send_message(message.chat.id,
                     'ok')
    sql_func(message)


def last_message(message):
    global sql
    global chat_id
    sql[message.chat.id] = "SELECT last_mess FROM users WHERE chat_id='%s'" % chat_id[message.chat.id]
    data = sql_func(message)
    bot.send_message(message.chat.id,
                     data[0]['last_mess'])


def block(message):
    global sql
    global chat_id
    global block_status
    block_bool = 1
    block_status = 'заблокирован'
    sql[message.chat.id] = 'SELECT user_block FROM users WHERE chat_id=%s' % chat_id[message.chat.id]
    data = sql_func(message)
    if data[0]['user_block'] == 1:
        block_bool = 0
        block_status = 'разблокирован'
    sql[message.chat.id] = "UPDATE users SET user_block=%s WHERE chat_id=%s" % (block_bool, chat_id[message.chat.id])
    sql_func(message)
    bot.send_message(message.chat.id,
                     'Пользователь %s' % block_status,
                     reply_markup=user_menu)
    return 24


def back_to_mm(message):
    bot.send_message(message.chat.id,
                     '🏢Главное меню🏢',
                     reply_markup=main_menu)
    return 0


def sql_func(message):
    try:
        bot_db.ping()
        cursor.execute(sql[message.chat.id])
    except pymysql.err.ProgrammingError as e:
        logs = open('market_bot(logs).txt', 'a')
        logs.write('%s . Time : %s\n\n' % (e.args[0], datetime.datetime.now()))
        logs.close()
    except pymysql.err.IntegrityError as e:
        logs = open('market_bot(logs).txt', 'a')
        logs.write('%s . Time : %s\n\n' % (e.args[0], datetime.datetime.now()))
        logs.close()
    finally:
        bot_db.commit()
        bot_db.close()
    data = cursor.fetchall()
    return data


bot.polling()
