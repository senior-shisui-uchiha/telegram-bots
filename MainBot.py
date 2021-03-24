import time
import telebot
import re
import pymysql


start_time = time.time()
token='token'
bot = telebot.TeleBot(token)
serverip="localhost"
login="login"
password="pass"
DataBase="db"
stady=0
#Main=Menu===============================================================================================================
ConnectToDBBut = telebot.types.InlineKeyboardButton('Connect to server', callback_data='connectdb')
CreateUserBut = telebot.types.InlineKeyboardButton('Create user', callback_data='usercreate')
MainButtons = telebot.types.InlineKeyboardMarkup()
MainButtons.add(ConnectToDBBut)
MainButtons.add(CreateUserBut)
#Change=Menu=============================================================================================================
DeleteBut = telebot.types.InlineKeyboardButton('Delete record from %s'%DataBase, callback_data='delete')
InsertBut = telebot.types.InlineKeyboardButton('Insert into %s'%DataBase, callback_data='insert')
ExitToMenuBut = telebot.types.InlineKeyboardButton('Back to Main Menu', callback_data='exit')
ShangeBut=telebot.types.InlineKeyboardMarkup()
ShangeBut.add(DeleteBut)
ShangeBut.add(InsertBut)
ShangeBut.add(ExitToMenuBut)
#Root=Menu================================================================================================================
test = telebot.types.InlineKeyboardButton('test', callback_data='test')
close = telebot.types.InlineKeyboardButton('close', callback_data='close')
sendcommand=telebot.types.InlineKeyboardButton('send command', callback_data='command')
RootMenu=telebot.types.InlineKeyboardMarkup()
RootMenu.add(test)
RootMenu.add(close)
RootMenu.add(sendcommand)


#BOT`S=FUNCTIONS===============================================================================================================================================================
def TryToConnect():
    try:
        db= pymysql.connect(host=serverip,user=login,password=password,db=DataBase,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
        cursor=db.cursor()
        return db,cursor
    except pymysql.err.IntegrityError as e:
        bot.send_message(id,e.args[1])


def ConnectToMySQL(id):
    db,cursor=TryToConnect()
    try:
        cursor.execute("show tables")
        db.commit()
        data = cursor.fetchall()
        for i in data:
            bot.send_message(id,str(i)[1:-1])
    finally:        
        db.close()
    bot.send_message(id, 'Edit Menu', reply_markup=ShangeBut)


def delete_from_table(msg):
    db,cursor=TryToConnect()
    msgtext=msg.text.split(' ')
    table,attribute=msgtext[0],msgtext[1]
    sql="delete from {0} where id={1}".format(table,attribute)
    try:
        cursor.execute(sql)
        db.commit()
    except pymysql.err.InternalError as e:
       bot.send_message(msg.chat.id,e.args[1])
    finally:        
        db.close()
    bot.send_message(msg.chat.id, 'Edit Menu', reply_markup=ShangeBut)
   

def insert_into_table(msg):
    db,cursor=TryToConnect()
    msgtext=msg.text.split(' ')
    table=msgtext[0]
    values=msgtext[1:-1]
    sql="insert into {0} values({1})".format(table,values)
    try:
        with db.cursor() as cursor:
            cursor.execute(sql)
            db.commit()
    except pymysql.err.InternalError as e:
        if e.args[1].startswith("Access denied for"):
            bot.send_message(msg.chat.id,e.args[1])
    finally:        
        db.close()
    bot.send_message(msg.chat.id, 'Edit Menu', reply_markup=ShangeBut)
   

def ip_read(msg):
    global serverip
    global stady
    stady+=1
    ip_check = re.findall("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", msg.text)
    if (ip_check == [])&(msg.text!="localhost"):
        bot.send_message(msg.chat.id,"Invalid IP - " + str(msg.text))
    else:
        serverip=msg.text
        bot.send_message(msg.chat.id,'Input Data Base name')


def dbname_read(msg):
    global DataBase
    global stady
    stady+=1
    DataBase=msg.text
    bot.send_message(msg.chat.id,'Connecting...')
    ConnectToMySQL(msg.chat.id)


def login_read(msg):
    global login
    global stady
    stady+=1
    login=msg.text
    bot.send_message(msg.chat.id,'Input password')


def password_read(msg):
    global password
    global stady
    stady+=1
    password=msg.text
    bot.send_message(msg.chat.id,'Main Menu', reply_markup=MainButtons)


def root_password(msg):
    if msg.text=='123456789':
        bot.send_message(msg.chat.id,'Root Menu',reply_markup=RootMenu)
#BUTTONS=FUNCTION============================================================================================================
def connectdb(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Input server`s ip")
    return 1
def usercreate(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Input login")
    return 3
def delete_but(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Input table name and id")
    return 5
def insert_but(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Input table name and values")
    return 6
def exit_to_menu(call):
    bot.send_message(call.message.chat.id, 'Main Menu', reply_markup=MainButtons)
    return 0
def test_connect(call):
    db,cursor=TryToConnect()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Try to connect oscar@localhost 1234 telega")
    try:
        cursor.execute("show tables")
        db.commit()
        data = cursor.fetchall()
        for i in data:
            bot.send_message(id,str(i)[1:-1])
    finally:        
        db.close()
def close_bot(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Bot is stop now  --- %s seconds ---"%(time.time() - start_time))
    bot.stop_polling()
    bot.stop_bot()
    exit()
def Send_Command(call):
    db,cursor=TryToConnect()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Input sql command")
    try:
        cursor.execute(sql)
    except pymysql.err.ProgrammingError as e:
        if e.args[1].startswith("You have an error in your SQL syntax"):
            bot.send_message(id,str(e.args[1]))
    finally:        
        db.close()
    #bot.send_message(chat_id=call.message.chat.id, 'Root Menu', reply_markup=RootMenu)



#BOT=========================================================================================================================
#WORK=WITH=BOT=================================================================================================================================================
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Main Menu', reply_markup=MainButtons)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global stady
    if call.message:
        buttons={'connectdb':connectdb,
                'usercreate':usercreate,
                'delete':delete_but,
                'insert':insert_but,
                'exit':exit_to_menu,
                'test':test_connect,
                'close':close_bot,
                'command':Send_Command}
        stady=buttons[call.data](call)


@bot.message_handler(content_types=['text'])
def send_text(message):
    global stady
    if stady>=1:
        functions={1:ip_read,2:dbname_read,3:login_read,4:password_read,5:delete_from_table,6:insert_into_table,7:root_password}
        functions[stady](message)    
    if message.text.lower() == 'hello':
        bot.send_message(message.chat.id,'Main Menu', reply_markup=MainButtons)
    elif message.text.lower() == 'connecting':
        bot.send_message(message.chat.id,'Connecting...')
        ConnectToMySQL(message.chat.id)
    elif message.text.lower() == 'root':
        bot.send_message(message.chat.id,'Input password')
        stady=7

