import telebot
from telebot import types
import datetime
import threading
#import schedule
from datetime import date
from datetime import datetime
import time
#import schedule
from queue import Queue
import xls_test
import sys
import json
#import schedule
from xls_test import get_tmrrw_tt, labs_tmrrw, start_xls
bot = telebot.TeleBot('8044042799:AAHx4S_SHMwAlA8XshkOuJh2I-_1sjZfdOg');

#ооздание очередей на этот же день - не рекомендовано (не критично)

users = list() #содержит элементы Susers
print("iteration")

bot.set_my_commands([
    telebot.types.BotCommand(command='panel', description='Панель администратора'),
    telebot.types.BotCommand(command='start', description='регистрация'),
    telebot.types.BotCommand(command='help', description='help')
])

print(f"Main thread, thread id = <{threading.current_thread().ident}>")

Admins = list() #список администраторов, хранит chat.id дминистраторов
#Suser = list() #список юзеров, хранит имя, id, статус: approved = 0 - not approved
#Wait_approv = Queue() #хранит список пользователей ожидающих подтверждения, после обработки юзер удаляется из очереди #не используется
Wait_approv_dict = dict() #словарь ожидающих подтверждения, ключ - номер в очереди, обьект - Suser
QueueS = {} #словарь очередей, ключ - номер пары по счету, обьект - очередь
UserQueueS = {}#пользовательские очереди, ключ - структура date_time - дата и время начала, обьект - список event который включает name и очередь Queue
#SuserNum = list() #Suser, num in queue
#Queue = list() #содержит SuserNum
#labs_tmrrw = dict() #содержит списки lab = list() #str (name), pair_num
UserQueueThreads = list() #список пользовательских потоков создания очереди



"""
start - перенаправляет на ввод фамилии enter_FIO -> new_user_waiting(добавление в Wait_approv_dict) и направляет запрос на подтверждение учетной записи всем администраторам 
InlineButtons ('approved','disapproved') -> callback_query_handler, удаляет сообщение с InlineButtons и создат обьект Suser + users.append(Suser)

panel -  перенаправляет на ввод пароля enter_password и (если правильный) добавляет id пользователя в список admins

export(admin) - ввод названия файла ->write_users_to_json->write_to_json

create - создает новый поток для каждой очереди, где создает очередь и ожидает ее начала останавливая этот же поток до ее начала
"""

def user_queue_deletion():
    print(f"entered user_deletion_thread, thread id = <{threading.current_thread().ident}>, len of UserQueueS = <{len(UserQueueS)}>")
    while True:# раз в 30 секунд проверяет, не появилась ли более ранняя очередь
        if len(UserQueueS) != 0:
            print("usQdelThread started")
            earliest_date = datetime(3000, 1, 1)
            for date in UserQueueS.keys():
                print(f"user_queue_deletion: key type in UserQueueS = {type(date)}, UserQueueS = {UserQueueS}")
                if date < earliest_date:
                   earliest_date = date
            print(f"earliest date: {earliest_date}") #полезная нагрузка (usQ_deletion_handler) перемещена в wait_until_datetime()
            wait_until_datetime(earliest_date) #добавить wait_until_datetime ##########################################

        time.sleep(30)
        """
                   schedule.at(earliest_date).do(usQ_deletion_handler(earliest_date))
                   while schedule.jobs:
                       schedule.run_pending()
                       time.sleep(1)
                       """

thread3 = threading.Thread(target=user_queue_deletion)
thread3.start()

print(f"currently existing threads: {threading.enumerate()}")

@bot.message_handler(commands=['panel'])
def panel(message):
    print(f"panel called")
    bot.send_message(message.chat.id, 'enter admin password')
    bot.register_next_step_handler(message, enter_password)

def enter_password(message):
    if message.text == '1234':
        bot.send_message(message.chat.id, 'correct password')
        is_alrd_admin = 0 #1 - already admin, 0 - register
        for admin in Admins:
            if message.chat.id == admin:
                is_alrd_admin = 1
                print("already admin")
                bot.send_message(message.chat.id, 'you have already been logged in as admin')
                return
        if is_alrd_admin == 0:
            Admins.append(message.chat.id)
            print(f"added new admin, id = {message.chat.id}")
            bot.send_message(message.chat.id, 'registred as a new admin\nAdmin functions:\n/help - view admin functions & support\n/create - create special queue\n/export - extract the list of users to json file\n/import - import a list of users from json file\nSupport:\n@IstrebitelNasvaya2013')
    else:
        bot.send_message(message.chat.id, 'wrong password')

@bot.message_handler(commands=['start'])
def start_message(message):
    print("user pressed start")
    is_alrd_registred = 0
    for user in users:
        if user[1] == message.chat.id:
            if user[2] == 1:
                is_alrd_registred = 1
                break
    if is_alrd_registred == 1:
        bot.send_message(message.chat.id, 'вы уже зарегистрированы')
    else:
        print(f"new user, ID: {message.chat.id}")
        bot.send_message(message.chat.id, 'ведите ФИО (функции изменения нет)')
        bot.register_next_step_handler(message, enter_FIO)
    #Suser = (chat_id, approved) #
    #users.append(Suser)
    #markup = types.InlineKeyboardMarkup()
    #btn1 = types.InlineKeyboardButton(text='Button 1', callback_data='btn1')
    #btn2 = types.InlineKeyboardButton(text='Button 2', callback_data='btn2')
    #markup.add(btn1, btn2)
    #bot.send_message(message.from_user.id, "По кнопке ниже можно перейти на сайт хабра", reply_markup=markup)

def enter_FIO(message): #еределать регистрацию через словарь
    bot.send_message(message.chat.id, 'Дождитесь подтверждения администратора')
    chat_id = message.chat.id
    approved = 0
    name = message.text
    Suser = list()
    Suser.append(name)
    Suser.append(chat_id)
    Suser.append(approved)
    key = new_user_waiting(Suser)
    print(Wait_approv_dict)
    #Wait_approv.put(Suser)
    for admin in Admins:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Approve', callback_data=f'approvement,{key}')
        btn2 = types.InlineKeyboardButton(text='Disapprove', callback_data=f'disapprovement,{key}')
        markup.add(btn1, btn2)
        bot.send_message(admin, f'new user waiting for approvement: {name}', reply_markup=markup)
def new_user_waiting(Suser):
    global Wait_approv_dict
    for i in range(50):
        if len(Wait_approv_dict) == 0:
            Wait_approv_dict[i] = Suser
            print(Wait_approv_dict)
            return i
        print(f"{i} == {Wait_approv_dict.keys()}")
        if i in Wait_approv_dict.keys(): #место занято
            print(f"{i} in keys")
        else:    #место в списке по номеру i свободно
            Wait_approv_dict[i] = Suser
            print(Wait_approv_dict)
            return i
    print("Dict is full")
    return 0

@bot.message_handler(commands=['help'])
def help_foo(message):
    is_alrd_admin = 0  # 1 - already admin, 0 - register
    for admin in Admins:
        if message.chat.id == admin:
            is_alrd_admin = 1
    if is_alrd_admin == 1:
        bot.send_message(message.chat.id,
                         'registred as a new admin\nAdmin functions:\n/help - view admin functions & support\n/create - create special queue\n/export - extract the list of users to json file\n/import - import a list of users from json file\nSupport:\n@IstrebitelNasvaya2013')
    else:
        bot.send_message(message.chat.id, 'Support:\n@IstrebitelNasvaya2013')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    # if message.text == "/start":
    # print("new user")
    if message.text == "/create":
        is_alrd_admin = 0  # 1 - already admin, 0 - register
        for admin in Admins:
            if message.chat.id == admin:
                is_alrd_admin = 1
        if is_alrd_admin == 1:
            print("create queue")
            bot.send_message(message.chat.id, "Введите название очереди")
            bot.register_next_step_handler(message, pair_num)
        else:
            bot.send_message(message.chat.id, "you're not an admin")
    elif message.text == "/export":
        is_alrd_admin = 0  # 1 - already admin, 0 - register
        for admin in Admins:
            if message.chat.id == admin:
                is_alrd_admin = 1
        if is_alrd_admin == 1:
            write_users_to_json(message)
    elif message.text == "/import":
        is_alrd_admin = 0  # 1 - already admin, 0 - register
        for admin in Admins:
            if message.chat.id == admin:
                is_alrd_admin = 1
        if is_alrd_admin == 1:
            read_users_from_json(message)

def write_users_to_json(message):
    bot.send_message(message.chat.id, 'enter the name of the file, where you want to extract users list (example.json)')
    bot.register_next_step_handler(message, write_to_json)
def write_to_json(message):
    try:
        with open(message.text, 'w') as json_file:
            global users
            print(f"file name = <{message.text}>")
            json.dump(users, json_file)
        bot.send_message(message.chat.id, f'successfully written users to {message.text}')
    except IOError:
        bot.send_message(message.chat.id,f'Incorrect name of the file or something went wrong')
    except Exception as e:
        print(f"Error: {e}")
def read_users_from_json(message):
    bot.send_message(message.chat.id, 'enter the name of the file, where you want to import users list from (example.json)')
    bot.register_next_step_handler(message, read_from_json)
def read_from_json(message):
    try:
        with open(message.text, 'r') as json_file:
            global users
            users.clear()
            users = json.load(json_file)
        bot.send_message(message.chat.id, f'successfully read users from {message.text}\n Users list:\n{users}')
    except:
        bot.send_message(message.chat.id, f'Incorrect name of the file or something went wrong')

@bot.callback_query_handler(func=lambda callback: True)
def check_callback_data(callback):
    data = callback.data.split(",")
    #print(f"data[0] = {data[0]}")
    message = callback.message
    date_ = datetime.fromtimestamp(message.date)
    date_ = date_.strftime('%Y.%m.%d')
    year_then, month_then, day_then =map(int, date_.split('.'))
    current_date = datetime.now().strftime('%Y-%m-%d')
    year, month, day = map(int, current_date.split('-'))
    print(f"bot sent you this message on {year_then, month_then, day_then}, and now {year, month, day}")
    if day > day_then or month > month_then or year > year_then:
        print("you pressed outdated button")
        bot.send_message(callback.message.chat.id, 'you pressed outdated button')
        return
    print("reached the start of logic")
    global Wait_approv_dict
    if data[0]  == 'approvement':
        #print("admin pressed approve")
        print("trying to delete")
        print(callback.message.text)
        print(f"message_id = <{callback.message.message_id}>")
        try:
            bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        except Exception as e:
            print(e)
        print("deleted")
        print(Wait_approv_dict)
        print(f"len = {len(Wait_approv_dict)}")
        if not Wait_approv_dict:
            print("Error: haven't created Wait_approv_dict")
        if len(Wait_approv_dict) == 0:
            bot.send_message(callback.message.chat.id, f'All users have been processed')
            return
        else:
            if int(data[1]) in Wait_approv_dict.keys():
                Suser = Wait_approv_dict[int(data[1])]
                del Wait_approv_dict[int(data[1])]
            else:
                bot.send_message(callback.message.chat.id, f'User have already been processed')
                return
            Suser[2] = 1
            print(Suser)
            users.append(Suser)
            bot.send_message(callback.message.chat.id, f'User {Suser[0]} approved')
            bot.send_message(Suser[1], f'Your account have been approved')
    if data[0]  == 'disapprovement':
        try:
            bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        except Exception as e:
            print(e)
        #global Wait_approv_dict
        print("deleted")
        if len(Wait_approv_dict) == 0:
            bot.send_message(callback.message.chat.id, f'All users have been processed')
        else:
            if int(data[1]) in Wait_approv_dict.keys():
                Suser = Wait_approv_dict[int(data[1])]
                del Wait_approv_dict[int(data[1])]
            else:
                bot.send_message(callback.message.chat.id, f'User have already been processed')
                return
            bot.send_message(callback.message.chat.id, f'User {Suser[0]} disapproved')
            bot.send_message(Suser[1], f'Your account have been disapproved')
            del Suser
    if data[0]  == 'register':   #Добавить проверку, есть ли уже юзер в очереди
        chat_id = callback.message.chat.id
        print(f"users = {users}")
        print(f"user {chat_id} called registration")
        amt_in_q = 0
        print(f"num of the queue = {data[1]}, type = {type(data[1])}")
        #########for testing purposes only############
        #for key in QueueS
        #########for testing purposes only############
        if data[2] == 'U':
            if str_to_datetime(data[1]) in UserQueueS:  # if event with datetime key exist in UserQueueS
                if len(UserQueueS[str_to_datetime(data[1])]) != 1:
                    print("found queue in UserQueueS")
                    queue = UserQueueS[str_to_datetime(data[1])][1]
                else:
                    print("no queues with this key")
                    queue = list()
                    UserQueueS[str_to_datetime(data[1])].append(queue)
                print(UserQueueS)
                print(queue)
        elif data[2] == 'S':
            if float(data[1]) in QueueS.keys():
                queue = QueueS[float(data[1])]
            else:
                queue = list()
                QueueS[float(data[1])] = queue
        else:
            print(f"Error: data[2] code error")
            print(f"data[2] = {data[2]}, type = {type(data[2])}")
        #queue = list()
        if not queue:
            print("queue is empty")
            amt_in_q = 0
        else:
            print("queue isn't empty")
            for SuserNum in queue:
                print(f"<{SuserNum[0][1]}> == <{chat_id}>")
                if SuserNum[0][1] == chat_id:
                    print("user already registred")
                    bot.send_message(chat_id, f'Вы уже зарегистрированы')
                    return
                print(f"id of user, stored in queue = {SuserNum[0][1]}, his num in queue = {SuserNum[1]}")
                #print(f"{SuserNum[0][1]}")
                amt_in_q = SuserNum[1]
                print(f"amt_in_q = {amt_in_q}")
        print(f"3 QueueS = {QueueS}")
        for Suser in users:
            print(f"user {Suser[1]}")
            if Suser[1] == chat_id:
                SuserNum = list()
                SuserNum.append(Suser)
                SuserNum.append(amt_in_q+1)
                queue.append(SuserNum)
                print(f"current queue statement: {queue}, {data[2]}")
                bot.send_message(chat_id, f'Вы успешно зарегистрированы\nВаше место в очереди: {amt_in_q+1}')
                print(f"4 QueueS = {QueueS}")
                if data[2] == 'S':
                    print(f"data[1] = <{data[1]}>, type = {type(data[1])}")
                    QueueS[float(data[1])] = queue
                elif data[2] == 'U':
                    print(f"data[1] = <{data[1]}>, type = {type(data[1])}")
                    data[1] = str_to_datetime(data[1])
                    #print(newDate)
                    print(f"data[1] = <{data[1]}>, type = {type(data[1])}")
                    print(f"type = {type(data[1])}")
                    print(f"wasd {data[1]}")
                    print(UserQueueS)
                    print(UserQueueS[data[1]]) #список(пустой) ложится в словарь сразу при создании и изменяется вместе с изменением queue, так ей присваивается ссылка на список из словаря
                    #UserQueueS[data[1]].append(queue) #ложим очередь в список event в словаре UserQueueS по ключу date_time
                    print(f"UserQueueS = <{UserQueueS}>")
                else:
                    print(f"data[2] code error")
                    print(f"data[2] = {data[2]}")
                break
    if data[0] == 'viewQueue':
        print("user called view")
        chat_id = callback.message.chat.id
        print(f"1 QueueS = {QueueS}")
        if data[2] == 'S' and not QueueS:
            print("QueueS is empty")
            bot.send_message(chat_id, f'No queues registred')
            return
        elif data[2] == 'U' and not UserQueueS:
            print("UserQueueS is empty")
            bot.send_message(chat_id, f'No queues registred')
            return
        else:
            print(f"(User)QueueS isn't empty, {data[1]}, {data[2]}")
            if data[2] == 'S':
                Queue = QueueS[float(data[1])]
            elif data[2] == 'U':
                print("wsdf")
                print(f"UserQueueS = {UserQueueS}")
                #print(f"fetching Queue from UserQueueS, key = {data[1]}, event = {UserQueueS[data[1]]}, Queue = {UserQueueS[data[1]][1]}")
                print(f" data[1] = <{data[1]}>")
                data[1] = str_to_datetime(data[1])
                print(f"len(UserQueueS[data[1]]) = {len(UserQueueS[data[1]])}")
                if len(UserQueueS[data[1]]) == 2:
                    print(1)
                    print(UserQueueS[data[1]])
                    event = UserQueueS[data[1]]
                    print(event) # 0 - name, 1 - queue
                    print(event[1])
                    print(event[0])
                    #print(UserQueueS[data[1][1]])
                    Queue = event[1]
                    print(Queue)
                else:
                    bot.send_message(chat_id, f'Queue is empty')
                    return
                #Queue = list()
            else:
                print("Error: code data[2] error")
            print(f"length of Queue = {len(Queue)}, Queue = {Queue}")
            if not Queue or len(Queue) == 0:
                print("Queue is empty")
                bot.send_message(chat_id, f'Queue is empty')
                return
            else:
                print(Queue)
                strin = data[3] + "\n"
                for SuserNum in Queue:
                    print(SuserNum)
                    print(type(SuserNum[1]))
                    print(type(SuserNum[0][0]))
                    buf1 = (SuserNum[1])
                    buf2 = SuserNum[0][0]
                    print(f"{buf1} {buf2}")
                    strin += str(buf1)
                    print(strin)
                    strin += " " + buf2 + "\n"
                print(strin)
                bot.send_message(chat_id, f'{strin}')

def str_to_datetime(string):
    i = 0
    for i in range(len(string)):
        if string[i] == ' ':  # i - index of space
            print(f"i = {i}")
            break
    print(f" i = {i}, <{string[:i]}><{string[i + 1:]}>")
    year, month, day = map(int, string[:i].split('-'))
    hour, minute, second = map(int, string[i + 1:].split(':'))
    print(f"year = {year}, month = {month}, day = {day}, hour = {hour}, minute = {minute}, second = {second}")
    newDateTime = datetime(year, month, day, hour, minute, second)
    return newDateTime
def wait_until_datetime(target_datetime):
    now = datetime.now()
    if now.year == target_datetime.year and now.month == target_datetime.month and now.day == target_datetime.day and now.hour == target_datetime.hour and now.minute == target_datetime.minute:
        print("thread started")
        print(f"continuing usQdelThread, thread id = <{threading.current_thread().ident}>")
        usQ_deletion_handler(target_datetime)
    else:
        time.sleep(10) # 0 IQ (у меня)
def wait_until_time(target_time, name):
    print(f"waiting until {target_time}")
    print(f"thread {name}, thread id = <{threading.current_thread().ident}>")
    while True:
        now = datetime.now()
        if now.hour == target_time.hour and now.minute == target_time.minute and now.second == target_time.second:
            print(f"thread {name} started, thread id = <{threading.current_thread().ident}>")
            break
        else:
            time.sleep(1)

#поток работы с расписанием из excel файла, использует функции из xls_test.py, начинается каждый день в 16:00
def scheduled_thread():
    while True:

        target_time = datetime.now()
        target_time = target_time.replace(hour=18, minute=59, second=59)
        wait_until_time(target_time, 'scheduled thread')
        ################for testing purposes only##################
        #print("Enter 1")
        #if int(input()) == 1:
        ################for testing purposes only##################
        print("started")
        start_xls()  # функция для первого запуска логики
        print(labs_tmrrw)
        for lab in labs_tmrrw:
            i = lab[1]
            for Suser in users:
                markup = types.InlineKeyboardMarkup()
                print(f"transmitting {i}, for lab {lab[0]}")
                btn3 = types.InlineKeyboardButton(text='Записаться', callback_data=f'register,{i},S,{lab[0]}')  # S - scheduled
                btn4 = types.InlineKeyboardButton(text='Посмотреть очередь', callback_data=f'viewQueue, {i},S,{lab[0]}')
                markup.add(btn3, btn4)
                bot.send_message(Suser[1], f'Очередь на {lab[0]}', reply_markup=markup)
        del_queue_2() # после окончания добавления новых лаб переходит в функцию удаления лаб
        print(QueueS)
        print(labs_tmrrw)

#вызывается во 2 потоке, после создания очередей и задерживает его до удаления каждой очереди по порядку на следующий день (час создания очереди - 16, часы удаления - с 9 до 16 след дня)

def send_queue(numOfQueue, name):
    for Suser in users:
        chat_id = Suser[1]
        print(f"sending queue to user {chat_id}")
        if not QueueS:
            print("QueueS is empty")
            bot.send_message(chat_id, f'No queues registred')
        else:
            print("QueueS isn't empty")
            if numOfQueue in QueueS:
                Queue = QueueS[numOfQueue]
                if not Queue:
                    print("Queue is empty")
                    bot.send_message(chat_id, f'Queue is empty')
                else:
                    print(f"Queue = <{Queue}>")
                    strin = name + '\n'
                    for SuserNum in Queue:
                        print(SuserNum)
                        print(type(SuserNum[1]))
                        print(type(SuserNum[0][0]))
                        buf1 = (SuserNum[1])
                        buf2 = SuserNum[0][0]
                        print(f"{buf1} {buf2}")
                        strin += str(buf1)
                        print(strin)
                        strin += " " + buf2 + "\n"
                    print("done")
                    print(strin)
                    bot.send_message(chat_id, f'{strin}')
            else:
                print(f"something went wrong, QueueS = {QueueS},  numOfQueue = {numOfQueue}")
#ожидает время начала каждой пары и вызывает deletion_handler_2
def del_queue_2():# сравнивает номер первой пары в labs_tmrrw пары со значением в match, пока не придет соответствующее время, после чего удаляет первый элемент
    i = 0 # i - индекс очереди
    while labs_tmrrw:
        _time = datetime.now()
        hour = _time.hour
        minute = _time.minute
        name = labs_tmrrw[0][0]
        p_num = labs_tmrrw[0][1]
        print(f"QueueS = {QueueS}")
        print(labs_tmrrw)
        print(f"hour = {hour}, minute = {minute}, pair_num = {p_num}")
        match p_num:
            case 1:
                if hour == 9:
                    deletion_handler_2(p_num, name)
            case 1.1:
                if hour == 9:
                    deletion_handler_2(p_num, name)
            case 2:
                if hour == 10 and minute == 30:
                    deletion_handler_2(p_num, name)
            case 2.1:
                if hour == 10 and minute == 30:
                    deletion_handler_2(p_num, name)
            case 3:
                if hour == 12 and minute == 25:
                    deletion_handler_2(p_num, name)
            case 3.1:
                if hour == 12 and minute == 25:
                    deletion_handler_2(p_num, name)
            case 4:
                if hour == 14:
                    deletion_handler_2(p_num, name)
            case 4.1:
                if hour == 14:
                    deletion_handler_2(p_num, name)
            case 5:
                if hour == 15 and minute == 50:
                    deletion_handler_2(p_num, name)
            case 5.1:
                if hour == 15 and minute == 50:
                    deletion_handler_2(p_num, name)
            case 6:
                if hour == 17 and minute == 25:
                    deletion_handler_2(p_num, name)
            case 6.1:
                if hour == 17 and minute == 25:
                    deletion_handler_2(p_num, name)
            case _:
                print("incorrect pair number")
        time.sleep(20)
#вызывает send_queue(шлет конечную очередь юзеру) удаляет очередь из списка Queue, удаляет лабу из labs_tmrrw
def deletion_handler_2(p_num, name):
    print(f"QueueS = {QueueS}")
    send_queue(p_num, name)  # посылаем индекс очереди
    if p_num in QueueS:
        del QueueS[p_num]
    del labs_tmrrw[0]
    print(f"QueueS = {QueueS}")
#функции для ввода инфы для создания пользовательской очереди
def pair_num(message):
    name = message.text
    bot.send_message(message.chat.id, "Введите время начала лабы/экзамена (в формате HH:MM)")
    bot.register_next_step_handler(message, lambda message: date_input(message, name ) )
def date_input(_time, name):
    print("entered date input")
    try:
        hour, minute = map(int, _time.text.split(':'))
    except ValueError:
        bot.send_message(_time.chat.id, "Input Error. Try again.\nВведите время начала лабы/экзамена (в формате HH:MM)")
        bot.register_next_step_handler(_time, lambda message: date_input(message, name))
        return
    bot.send_message(_time.chat.id, "Введите дату (в формате YYYY-MM-DD):")
    bot.register_next_step_handler(_time, lambda message: user_queue(message, name, hour, minute))
def user_queue(date, name, hour, minute): #третьим параметром передать в обработчик кнопок, что очередь пользовательская
    try:
        year, month, day = map(int, date.text.split('-'))
    except ValueError:
        bot.send_message(date.chat.id, "Error.Incorrect input.\nВведите дату (в формате YYYY-MM-DD):")
        bot.register_next_step_handler(date, lambda message: user_queue(message, name, hour, minute))
        return
    now = datetime.now()
    if year < now.year or year == now.year and month < now.month or year == now.year and month == now.month and day < now.day:
        bot.send_message(date.chat.id, "Error.Incorrect input.\nCant create queue in the past\nВведите дату (в формате YYYY-MM-DD):")
        bot.register_next_step_handler(date, lambda message: user_queue(message, name, hour, minute))
        return
    if year == now.year and month == now.month and day == now.day:
        #if hour < now.hour or hour == now.hour and minute <= now.minute+5:
        if hour < now.hour or hour == now.hour and minute <= now.minute + 1: #for testing
            bot.send_message(date.chat.id,"Input Error.\nCant create queue earlier than 5 minutetes before the deadline\n Try again.\nВведите время начала лабы/экзамена (в формате HH:MM)")
            bot.register_next_step_handler(date, lambda message: date_input(message, name))
            return
    date_time = datetime(year, month, day, hour, minute)
    #bot.send_message(date.chat.id, "Очередь создана, до начала регистрации, создание ")
    if not UserQueueS:
        print("user queues are empty")
        event = list()
    else:
        if date_time not in UserQueueS:
            event = list()
            #UserQueueS[date_time] = list()
        else:
            bot.send_message(date.chat.id, "В этот день в это время уже существует событие")
            return
    event.append(name)
    UserQueueS[date_time] = event
    print(UserQueueS[date_time])
    if datetime.now().minute > 54:
        start_minute = datetime.now().minute - 55
        start_hour = datetime.now().hour+1 #for testing
    else:
        #start_minute = datetime.now().minute+5
        start_minute = datetime.now().minute + 1 #for testing
        start_hour = datetime.now().hour
    for Suser in users:
        bot.send_message(Suser[1], f"Очередь на {name}, {date_time}\nрегистрация начнется  {start_hour}:{start_minute}")

    #time.sleep(300)
    usQregThread = threading.Thread(target=usQregStart(start_minute, start_hour, date_time, name)) # конечный поток
    usQregThread.start()
    UserQueueThreads.append(usQregThread)
    print(f"currently existing threads: {threading.enumerate()}")
#функция создания пользовательской очереди из потока обработчике /create(pair_num->date_input->user_queue)
def usQregStart(start_minute, start_hour, date_time, name):
    print("smth")
    print(f"usQregThread started, start_hour = {start_hour}, start_minute = {start_minute}")
    #while datetime.now().minute == start_minute and datetime.now().hour == start_hour:#закинуть в отдельный поток
    target_time = datetime(2024, 10, 10,hour=start_hour, minute=start_minute, second=0)
    print(f"target_time = {target_time}")
    wait_until_time(target_time, 'usQregStart')#################################################################################
    print(f"continuing usQregThread,thread id = <{threading.current_thread().ident}>")
    for Suser in users:
        markup = types.InlineKeyboardMarkup()
        print(f"transmitting {date_time}, for lab {name}")
        btn3 = types.InlineKeyboardButton(text='Записаться', callback_data=f'register,{date_time},U,{name}')  # U - user made
        btn4 = types.InlineKeyboardButton(text='Посмотреть очередь', callback_data=f'viewQueue,{date_time},U,{name}')
        markup.add(btn3, btn4)
        bot.send_message(Suser[1], f'Очередь на {name}', reply_markup=markup)
    print(f"end of usQregThread, thread id = <{threading.current_thread().ident}>")
    #sys.exit() #эта хуйня она все портит #############################################

thread = threading.Thread(target=scheduled_thread) # бесконечный поток - читает файл, создает, удаляет
thread.start()

#просмотр всех существующих потоков и удаление уже завершившихся
def show_current_threads():
    while True:
        for thread in UserQueueThreads:
            thread.join(timeout=1)#ожидание завершения каждого потока не более 1 секунды
        print(f"this thread id = <{threading.current_thread().ident}>")
        print(f"currently existing threads: {threading.enumerate()}")
        time.sleep(60)

thread4 = threading.Thread(target=show_current_threads)
thread4.start()
#функция удаления пользовательской очереди из потока обработчике /create(pair_num->date_input->user_queue)  + в ней же идет ожидание начала eventа
def usQ_deletion_handler(date):
    print(f"user_deletion_handler called, thread id = <{threading.current_thread().ident}>")
    print(f"UserQueueS = {UserQueueS}, length = {len(UserQueueS)}")
    if len(UserQueueS[date]) == 1:
        print("UserQueue is empty")
        strin = "Queue is empty"
    else:
        print(f"{UserQueueS[date][0]} - name, {UserQueueS[date][1]} - Queue = list()")
        Queue  = UserQueueS[date][1]
    #if not Queue:
     #   print("Queue is empty")
       # strin = "Queue is empty"
    #else:
        print(Queue)
        strin = ""
        for SuserNum in Queue:
            print(SuserNum)
            print(type(SuserNum[1]))
            print(type(SuserNum[0][0]))
            buf1 = (SuserNum[1])
            buf2 = SuserNum[0][0]
            print(f"{buf1} {buf2}")
            strin += str(buf1)
            print(strin)
            strin += " " + buf2 + "\n"
        print(strin)
    for Suser in users:
        bot.send_message(Suser[1], f'Очередь на {UserQueueS[date][0]}.\nрегистрация завершена\n{strin}')
    del UserQueueS[date]

"""
print("polling")
if __name__ == '__main__':
  while True:
    try:
      bot.polling(none_stop=True)
    except:
      time.sleep(0.3)
"""
#при создании двух пользовательских очередей главный поток спит и не дает зарегистрироваться
# подтверждено, что-то с потоками, что-то занимает главный поток
#две послед очереди тоже не ворк
# проверить потоки




