import telebot
import pymysql
import random
from datetime import datetime
import requests


token = '1024091588:AAFYiRd5sm5z4Ol2aF1lxFqayR8o1XNxIo0'
bot = telebot.TeleBot(token)
server_ip = 'localhost'
login = "telegrambotadmin"
password = "botparol00115566"
database = 'market_bot'
step = 1
admin_chat_id = '0'
sql_dict = {}
errors_array = []
energy = {}
cost_dict = {}
minus_energy_time = datetime.now()
plus_energy_time = datetime.now()


bot_db = pymysql.connect(host=server_ip,
                         user=login,
                         password=password,
                         db=database,
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)
cursor = bot_db.cursor()
sql = 'SELECT energy,chat_id FROM users'
bot_db.ping()
cursor.execute(sql)
energy_data = cursor.fetchall()
for j in energy_data:
    energy[j['chat_id']] = j['energy']


main_menu = telebot.types.ReplyKeyboardMarkup(True)
main_menu.add('🎒Инвентарь🎒', '⚖️Рынок⚖️')\
         .add('🏹Арена🏹')\
         .add('👩‍🦰Реферальная компания👨‍🦰')


market_menu = telebot.types.ReplyKeyboardMarkup(True)
market_menu.add('💵Купить💵')\
           .add('💰Продать💰')\
           .add('🏢Назад в главное меню🏢')


buy_menu = telebot.types.ReplyKeyboardMarkup(True)
buy_menu.add('🦺Броня🦺')\
        .add('🏹Оружие🏹', '🧤Перчатки🧤')\
        .add('👖Штаны👖', '🥾Сапоги🥾')\
        .add('🏢Назад в главное меню🏢')


ref_menu = telebot.types.ReplyKeyboardMarkup(True)
ref_menu.add('🧍‍♀️Мои рефералы🧍')\
        .add('📃Моя реферальная ссылка📃')\
        .add('🏢Назад в главное меню🏢')


@bot.message_handler(commands=['start'])
def start_message(message):
    global sql_dict
    global step
    global errors_array
    current_date = '%s' % str(datetime.now().date())[:11]
    step = 0
    sql_dict[message.chat.id] = "select user_id from users where chat_id=%s" % message.chat.id
    energy[message.chat.id] = 300
    data = sql_func(message)
    if data == ():
        ref_id = 0
        if message.text != '/start':
            ref_id = message.text[7:]
            bot.send_message(message.text[7:],
                             'По вашей ссылке зарегестрировался пользователь %s %s' % (message.from_user.first_name,
                                                                                       message.from_user.last_name))
        sql_dict[message.chat.id] = "INSERT INTO users(chat_id," \
                                    "speed," \
                                    "armour," \
                                    "health," \
                                    "user_name," \
                                    "user_money," \
                                    "ref_id," \
                                    "energy," \
                                    "start_data) VALUES('%s',100,20,200,'%s',200,'%s', 300, %s);" % (message.chat.id,
                                                                                                     '%s %s' % (message.from_user.first_name, message.from_user.last_name),
                                                                                                     ref_id,
                                                                                                     current_date)
        sql_func(message)
    step = 1
    back_to_mm(message)


@bot.message_handler(content_types=['text'])
def send_text(message):
    global step
    global sql_dict
    time = '%s' % datetime.now().time()
    sql_dict[message.chat.id] = "UPDATE users SET last_mess='%s' WHERE chat_id='%s'" % (time,
                                                                                        message.chat.id)
    sql_func(message)
    sql_dict[message.chat.id] = "SELECT user_block FROM users WHERE chat_id=%s" % message.chat.id
    data = sql_func(message)
    if data[0]['user_block'] == 1:
        bot.send_message(message.chat.id,
                         'Вы заблокированы администрацией')
    else:
        step_functions = {10: clothes_in_out,
                          22: code_read,
                          220: new_cost,
                          211: buy_item_func}
        functions = {'🎒Инвентарь🎒': look_inv_func,
                     '⚖️Рынок⚖️': buy_or_sell_items_func,
                     '🏹Арена🏹': area_func,
                     '💵Купить💵': buy_func,
                     '🦺Броня🦺': buy_type_func,
                     '🏹Оружие🏹': buy_type_func,
                     '🥾Сапоги🥾': buy_type_func,
                     '🧤Перчатки🧤': buy_type_func,
                     '👖Штаны👖': buy_type_func,
                     '💰Продать💰': sell_items_func,
                     '👩‍🦰Реферальная компания👨‍🦰': ref_menu_func,
                     '🧍‍♀️Мои рефералы🧍': my_ref,
                     '📃Моя реферальная ссылка📃': ref_code,
                     '🏢Назад в главное меню🏢': back_to_mm}
        if message.text in functions:
            try:
                step = functions[message.text](message)
            except KeyError:
                bot.send_message(0,
                                 'Я тебя не совсем понял 🙃 \nНажми нужную кнопку меню.')
                step = functions['🏢Назад в главное меню🏢'](message)
        elif step in step_functions:
            step = step_functions[step](message)


#####################################################################################################################################################################################
# ФУНКЦИИ ИНВЕНТАРЯ #################################################################################################################################################################
#####################################################################################################################################################################################


def look_inv_func(mess):
    global sql_dict
    global errors_array
    global minus_energy_time
    global plus_energy_time
    global energy
    sql_dict[mess.chat.id] = 'SELECT energy FROM users WHERE chat_id=%s' % mess.chat.id
    data = sql_func(mess)
    energy[mess.chat.id] = data[0]['energy']
    if energy[mess.chat.id] < 300:
        plus_energy_time = datetime.now()
        time_between = (plus_energy_time - minus_energy_time).total_seconds()
        plus_energy = int(time_between / 30)
        energy[mess.chat.id] += plus_energy
        sql_dict[mess.chat.id] = 'update users set energy=%s where chat_id=%s' % (energy[mess.chat.id],
                                                                                  mess.chat.id)
        sql_func(mess=mess)
        while time_between >= 30:
            minus_energy_time = datetime.now()
            time_between -= 30
        bot.send_message(mess.chat.id,
                         'Следуещее востановление ⚡️%sc. $' % int(30 - time_between))
        if energy[mess.chat.id] > 300:
            energy[mess.chat.id] -= (energy[mess.chat.id] - 300)
            sql_dict[mess.chat.id] = 'update users set energy=%s where chat_id=%s' % (energy[mess.chat.id],
                                                                                      mess.chat.id)
            sql_func(mess=mess)
    bot.send_message(mess.chat.id,
                     'У вас %s ⚡️' % energy[mess.chat.id])
    money = output_money(mess)
    bot.send_message(mess.chat.id,
                     'У вас на счету %s 💴' % money)
    sql_dict[mess.chat.id] = "select * from inventory where user_id='%s'" % mess.chat.id
    data = sql_func(mess)
    if data == ():
        bot.send_message(mess.chat.id,
                         'У вас нет предметов в инвентаре')
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
                bot.send_message(mess.chat.id,
                                 output)
                output = ''
                k = 0
        if k < 10:
            bot.send_message(mess.chat.id,
                             output)
        bot.send_message(mess.chat.id,
                         'Введите код после | чтобы надеть/снять предмет')
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


def output_money(mess):
    global sql_dict
    global errors_array
    sql_dict[mess.chat.id] = "select * from users where chat_id='%s'" % mess.chat.id
    data = sql_func(mess=mess)
    money = data[0]['user_money']
    return money


def clothes_in_out(message):
    global sql_dict
    sql_dict[message.chat.id] = "SELECT * FROM inventory WHERE buy_code='%s' and user_id=%s" % (message.text,
                                                                                                message.chat.id)
    data = sql_func(message)
    message_text = 'Вы надели предмет'
    on_user = 1
    if data == ():
        bot.send_message(message.chat.id,
                         'Неверный код предмета')
    else:
        if data[0]['on_user'] == 1:
            message_text = 'Вы сняли предмет'
            on_user = 0
        else:
            sql_dict[message.chat.id] = "UPDATE inventory SET on_user=0 WHERE item_type='%s'" % data[0]['item_type']
            sql_func(message)
        bot.send_message(message.chat.id,
                         '%s   %s %s' % (message_text,
                                         data[0]['item_name'],
                                         data[0]['item_type']))
        sql_dict[message.chat.id] = "UPDATE inventory SET on_user=%s where buy_code='%s' and user_id=%s" % (on_user,
                                                                                                            message.text,
                                                                                                            message.chat.id)
        sql_func(message)
    return 110


#####################################################################################################################################################################################
# ПОКУПКА ВЕЩЕЙ  ####################################################################################################################################################################
#####################################################################################################################################################################################


def buy_or_sell_items_func(mess):
    bot.send_message(mess.chat.id,
                     '💴Торговая площадка💴',
                     reply_markup=market_menu)
    return 20


def buy_func(mess):
    bot.send_message(mess.chat.id,
                     'Выберите тип интересуещего предмета',
                     reply_markup=buy_menu)
    return 21


def buy_type_func(mess):
    global sql_dict
    global errors_array
    sql_dict[mess.chat.id] = 'SELECT inv_id FROM inventory WHERE user_id=%s' % mess.chat.id
    data = sql_func(mess)
    if len(data) >= 12:
        bot.send_message(mess.chat.id,
                         'Ваш инвентарь переполнен')
        return 0
    item_type = mess.text
    sql_dict[mess.chat.id] = "select * from inventory where item_type='%s' and on_market=1 and user_id!=%s;" % (item_type, mess.chat.id)
    data = sql_func(mess=mess)
    if data == ():
        bot.send_message(mess.chat.id,
                         "На продаже ничего нет в этой категории")
        return 210
    else:
        item_type_buy(mess=mess,
                      data=data)
    return 211


def item_type_buy(mess, data):
    stikers = {'🦺Броня🦺': '🦺',
               '🏹Оружие🏹': '🏹',
               '🥾Сапоги🥾': '🥾',
               '🧤Перчатки🧤': '⚡',
               '👖Штаны👖': '💚'}
    k = 0
    text = ''
    for i in range(len(data)):
        text += '%s (%s) %s(%s) Цена = %s | %s\n\n' % (data[i]['item_name'],
                                                       mess.text,
                                                       stikers[data[i]['item_type']],
                                                       data[i]['item_power'],
                                                       data[i]['item_cost'],
                                                       data[i]['buy_code'])
        k += 1
        if k == 10:
            bot.send_message(mess.chat.id,
                             text)
            k = 0
            text = ''
    if k < 10:
        bot.send_message(mess.chat.id,
                         text)
    bot.send_message(mess.chat.id,
                     'Введите код после | чтобы выбрать желаемый предмет')


def buy_item_func(message):
    global sql_dict
    money = output_money(message)
    sql_dict[message.chat.id] = "select item_cost from inventory where buy_code='%s'" % message.text
    data = sql_func(mess=message)
    if data == ():
        bot.send_message(message.chat.id,
                         'Неверный код предмета')
    else:
        cost = data[0]['item_cost']
        if cost > money:
            bot.send_message(message.chat.id,
                             'У вас не хватает денег на этот предмет')
        else:
            sql_dict[message.chat.id] = "SELECT * FROM inventory WHERE buy_code='%s'" % message.text
            data = sql_func(mess=message)
            sql_dict[message.chat.id] = "SELECT * FROM users WHERE chat_id=%s" % int(data[0]['user_id'])
            data = sql_func(mess=message)
            seller_chat_id = data[0]['chat_id']
            money_seller = data[0]['user_money']
            money_seller += cost
            sql_dict[message.chat.id] = "UPDATE users SET user_money = %s WHERE chat_id = %s" % (money_seller,
                                                                                                 data[0]['chat_id'])
            sql_func(message)
            money_after_buy = money - cost
            sql_dict[message.chat.id] = "UPDATE users SET user_money = %s WHERE chat_id = %s" % (money_after_buy,
                                                                                                 message.chat.id)
            sql_func(message)
            sql_dict[message.chat.id] = "UPDATE inventory SET user_id='%s',on_market=0,on_user=0 WHERE buy_code='%s'" % (message.chat.id,
                                                                                                                         message.text)
            sql_func(message)
            sql_dict[message.chat.id] = "SELECT * FROM inventory WHERE buy_code='%s'" % message.text
            data = sql_func(message)
            bot.send_message(message.chat.id,
                             'Вы купили %s %s' % (data[0]['item_name'],
                                                  data[0]['item_type']))
            try:
                bot.send_message(seller_chat_id,
                                 'Ваш предмет %s %s купили' % (data[0]['item_name'],
                                                               data[0]['item_type']))
            except telebot.apihelper.ApiTelegramException as e:
                logs = open('market_bot(logs).txt', 'a')
                logs.write('%s . Time : %s\n\n' % (e.args[0], datetime.now()))
                logs.close()
    return 2110


#####################################################################################################################################################################################
# ПРОДАЖА ВЕЩЕЙ  ####################################################################################################################################################################
#####################################################################################################################################################################################


def sell_items_func(mess):
    global sql_dict
    sql_dict[mess.chat.id] = "select * from inventory where user_id=%s;" % mess.chat.id
    data = sql_func(mess=mess)
    if data == ():
        bot.send_message(mess.chat.id,
                         'Вам нечего продать')
        return 1
    else:
        stikers = {'🦺Броня🦺': '🦺',
                   '🏹Оружие🏹': '🏹',
                   '🥾Сапоги🥾': '🥾',
                   '🧤Перчатки🧤': '⚡',
                   '👖Штаны👖': '💚'}
        k = 0
        text = ''
        for i in range(len(data)):
            market_status = 'Не продаеться'
            if data[i]['on_market'] == 1:
                market_status = 'На продаже'
            text += '%s (%s) %s(%s) | %s (%s)\n\n' % (data[i]['item_name'],
                                                      data[i]['item_type'],
                                                      stikers[data[i]['item_type']],
                                                      data[i]['item_power'],
                                                      data[i]['buy_code'],
                                                      market_status)
            k += 1
            if k == 10:
                bot.send_message(mess.chat.id,
                                 text)
                k = 0
        if k < 10:
            bot.send_message(mess.chat.id,
                             text)
        bot.send_message(mess.chat.id,
                         'Введите код после | чтобы выбрать предмет который хотите продать или снять с продажи')
    return 22


def code_read(message):
    global cost_dict
    global sql_dict
    sql_dict[message.chat.id] = "SELECT on_market FROM inventory WHERE buy_code='%s'" % message.text
    data = sql_func(message)
    if data == ():
        bot.send_message(message.chat.id,
                         'Неверный код предмета')
        bot.send_message(message.chat.id,
                         'Введите код после | чтобы выбрать предмет который хотите продать')
        return 22
    elif data[0]['on_market'] == 1:
        sql_dict[message.chat.id] = "UPDATE inventory SET on_market=0 WHERE buy_code='%s'" % message.text
        sql_func(message)
        bot.send_message(message.chat.id,
                         'Предмет снят с продажи')
    else:
        cost_dict[message.chat.id] = message.text
        bot.send_message(message.chat.id,
                         'Введите новую цену на этот предмет (минимум 1 , максимум 1000000000')
    return 220


def new_cost(message):
    global cost_dict
    global sql_dict
    if int(message.text) > 1000000000:
        bot.send_message(message.chat.id,
                         'Неверно указана цена, Повторите попытку')
        return 220
    else:
        sql_dict[message.chat.id] = "UPDATE inventory SET on_market=1, item_cost=%s WHERE buy_code='%s'" % (message.text,
                                                                                                            cost_dict[message.chat.id])
        sql_func(mess=message)
        sql_dict[message.chat.id] = "SELECT item_name,item_type FROM inventory WHERE buy_code='%s'" % cost_dict[message.chat.id]
        data = sql_func(mess=message)
        bot.send_message(message.chat.id,
                         'Вы выставили на продажу %s %s' % (data[0]['item_name'],
                                                            data[0]['item_type']))
        return 221


#####################################################################################################################################################################################
# АРЕНА  ############################################################################################################################################################################
#####################################################################################################################################################################################


def area_func(mess):
    global energy
    global minus_energy_time
    if energy[mess.chat.id] < 100:
        bot.send_message(mess.chat.id,
                         'У вас недостаточно энергии (%s)' % energy[mess.chat.id])
    else:
        minus_energy_time.now()
        energy[mess.chat.id] -= 100
        sql_dict[mess.chat.id] = 'update users set energy=%s where chat_id=%s' % (energy[mess.chat.id],
                                                                                  mess.chat.id)
        sql_func(mess=mess)
        bot.send_message(mess.chat.id,
                         '-100 ⚡️')
        generate_item(mess=mess)
    return back_to_mm(mess=mess)


def generate_item(mess):
    global sql_dict
    sql_dict[mess.chat.id] = 'SELECT inv_id FROM inventory WHERE user_id=%s' % mess.chat.id
    data = sql_func(mess)
    if len(data) >= 12:
        bot.send_message(mess.chat.id,
                         'Ваш инвентарь переполнен')
        return 1
    name_array = ['Бронзов',
                  'Серебрян',
                  'Алмазн',
                  'Железн']
    type_dic = {1: 'ая 🦺Броня🦺',
                2: 'ое 🏹Оружие🏹',
                3: 'ые 🥾Сапоги🥾',
                4: 'ые 🧤Перчатки🧤',
                5: 'ые 👖Штаны👖'}
    item = '%s%s %s' % (name_array[random.randint(0, 3)],
                        type_dic[random.randint(1, 5)],
                        random.randint(30, 130))
    for_sql = item.split(' ')
    sql_dict[mess.chat.id] = "INSERT INTO inventory(buy_code,item_name,item_power, item_cost ,user_id, item_type, on_market,on_user) VALUES ('0','%s', %s, 100, %s, '%s', 0, 0)" % (for_sql[0],
                                                                                                                                                                                    for_sql[2],
                                                                                                                                                                                    mess.chat.id,
                                                                                                                                                                                    for_sql[1])
    sql_func(mess=mess)
    sql_dict[mess.chat.id] = "UPDATE inventory set buy_code ='buy_%s' WHERE inv_id=%s" % (cursor.lastrowid,
                                                                                          cursor.lastrowid)
    sql_func(mess=mess)
    bot.send_message(mess.chat.id,
                     'Вы получили : "%s %s"' % (for_sql[0],
                                                for_sql[1]))
    return 1


#####################################################################################################################################################################################
# РЕФЕРАЛЬНОЕ МЕНЮ  #################################################################################################################################################################
#####################################################################################################################################################################################


def ref_menu_func(mess):
    bot.send_message(mess.chat.id,
                     '👩‍🦰Реферальная компания👨‍🦰',
                     reply_markup=ref_menu)
    return 4


def my_ref(mess):
    global sql_dict
    sql_dict[mess.chat.id] = "select * from users where ref_id='%s'" % mess.chat.id
    data = sql_func(mess=mess)
    if data == ():
        bot.send_message(mess.chat.id,
                         'У вас еще нет рефералов')
    else:
        for i in data:
            bot.send_message(mess.chat.id,
                             '%s' % i['user_name'])
    return 41


def ref_code(mess):
    bot.send_message(mess.chat.id,
                     "https://t.me/mysql273bot?start=%s" % mess.chat.id,
                     reply_markup=ref_menu)
    return 42


def back_to_mm(mess):
    bot.send_message(mess.chat.id,
                     '🏢Главное меню🏢',
                     reply_markup=main_menu)
    return 1


def sql_func(mess):
    try:
        bot_db.ping()
        cursor.execute(sql_dict[mess.chat.id])
    except pymysql.err.ProgrammingError as e:
        logs = open('market_bot(logs).txt', 'a')
        logs.write('%s . Time : %s\n\n' % (e.args[0], datetime.now()))
        logs.close()
    except pymysql.err.IntegrityError as e:
        logs = open('market_bot(logs).txt', 'a')
        logs.write('%s . Time : %s\n\n' % (e.args[0], datetime.now()))
        logs.close()
    finally:
        bot_db.commit()
        bot_db.close()
    data = cursor.fetchall()
    return data


try:
    bot.polling()
except requests.exceptions.ConnectionError as error:
    Logs = open('market_bot(logs).txt', 'a')
    Logs.write('%s . Time : %s\n\n' % (error.args[0], datetime.now()))
    Logs.close()
