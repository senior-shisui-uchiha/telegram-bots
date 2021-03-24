import pymysql


users = 'create table users(user_id int not null AUTO_INCREMENT,' \
        'user_block bool,' \
        'last_mess varchar(15),' \
        'start_data varchar (15),' \
        'speed int,' \
        'armour int,' \
        'health int,' \
        'energy int,' \
        'chat_id int,' \
        'user_name varchar(30),' \
        'user_money int,' \
        'ref_id int,' \
        'primary key(user_id));'


inventory = 'create table inventory(inv_id int not null AUTO_INCREMENT,' \
            'buy_code varchar (10),' \
            'item_name varchar(50),' \
            'item_power int,' \
            'item_cost int,' \
            'user_id int,' \
            'item_type varchar(10),'\
            'on_market bool,' \
            'on_user bool,' \
            'primary key(inv_id));'


bot_db = pymysql.connect(host='localhost',
                         user='telegrambotadmin',
                         password='botparol00115566',
                         db='market_bot',
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)
try:
    cursor = bot_db.cursor()
    cursor.execute(users)
    cursor.execute(inventory)
except pymysql.err.IntegrityError as e:
    print(e.args[1])
except pymysql.err.ProgrammingError as e:
    if e.args[1].startswith("You have an error in your SQL syntax"):
        print(str(e.args[1]))
finally:
    bot_db.commit()
    bot_db.close()
