#  Telegram bot version 0.1

from pymongo import MongoClient
import apiai
import json
import telebot
import constant
from datetime import datetime
from bot_logging import BotTLog
from time import sleep
from requests import exceptions
import billing_api
from router_get_info import RouterInfo
from subprocess import run

bot_t = telebot.TeleBot(constant.telegram)  # Set bot object

print(bot_t.get_me())  # print basic info about bot

messages_dict = {}  # Dictionary with key-message_id and message text
login_message_id = 0
pass_message_id = 0
mongo = MongoClient()
log = mongo.bot_t.log
access = mongo.bot_t.access
login_pass = mongo.bot_t.login_pass


@bot_t.message_handler(commands=['start'])
def handle_start(message):
    user_kays = telebot.types.ReplyKeyboardMarkup(True, False)
    user_kays.row('/check_equipment', '/info')
    user_kays.row('/cancel', '/login', '/payment')
    user_kays.row('/functions', '/book_installation')
    answer = bot_t.send_message(message.from_user.id, text=constant.start_message, reply_markup=user_kays)
    BotTLog().log_bot(answer.__dict__)
    BotTLog().log_user(message)


@bot_t.message_handler(commands=['check_equipment'])
def handle_equipment(message):
    if access.find_one({'chat_id': message.chat.id}) is not None:
        user_kays = telebot.types.ReplyKeyboardMarkup(True, False)
        user_kays.row('/ping', '/check_speed')
        # user_kays.row('/general_check')
        # user_kays.row('/wifi_diagnostic')
        answer = bot_t.send_message(message.from_user.id, text='What you would like to check', reply_markup=user_kays)
    else:
        answer = bot_t.send_message(message.from_user.id, text=constant.please_login)
    BotTLog().log_bot(answer.__dict__)
    BotTLog().log_user(message)


@bot_t.message_handler(commands=['check_speed'])
def handle_check_speed(message):
    if access.find_one({'chat_id': message.chat.id}) is not None:
        answer1 = bot_t.send_message(message.from_user.id, text=constant.second)
        answer2 = bot_t.send_message(message.from_user.id, text=RouterInfo.speed(access.find_one(
                                    {'chat_id': message.chat.id})['bill']))
        BotTLog().log_bot(answer2.__dict__)
    else:
        answer1 = bot_t.send_message(message.from_user.id, text=constant.please_login)
    BotTLog().log_bot(answer1.__dict__)
    BotTLog().log_user(message)


@bot_t.message_handler(commands=['ping'])
def handle_ping(message):
    if access.find_one({'chat_id': message.chat.id}) is not None:
        answer = bot_t.send_message(message.from_user.id, text=RouterInfo.ping(access.find_one({'chat_id': message.chat.id})
                                                                               ['bill']))
    else:
        answer = bot_t.send_message(message.from_user.id, text=constant.please_login)
    BotTLog().log_bot(answer.__dict__)
    BotTLog().log_user(message)


@bot_t.message_handler(commands=['book_installation'])
def handle_book(message):
    answer = bot_t.send_message(message.from_user.id, text=constant.booking_url)
    BotTLog().log_bot(answer.__dict__)
    BotTLog().log_user(message)


@bot_t.message_handler(commands=['info'])
def handle_payment(message):
    answer = bot_t.send_message(message.from_user.id, text=constant.info)
    BotTLog().log_bot(answer.__dict__)
    BotTLog().log_user(message)


@bot_t.message_handler(commands=['payment'])
def handle_payment(message):
    answer = bot_t.send_message(message.from_user.id, text=constant.payment_option)
    BotTLog().log_bot(answer.__dict__)
    BotTLog().log_user(message)


@bot_t.message_handler(commands=['functions'])
def handle_functions(message):
    answer = bot_t.send_message(message.from_user.id, text=constant.func)
    BotTLog().log_bot(answer.__dict__)
    BotTLog().log_user(message)


@bot_t.message_handler(commands=['bank'])
def handle_bank(message):
    answer = bot_t.send_message(message.from_user.id, text=constant.bank_ditails)
    BotTLog().log_bot(answer.__dict__)
    BotTLog().log_user(message)


@bot_t.message_handler(commands=['Logging_in'])  # Logging in command
def handle_logging_in(message):
    user_kays = telebot.types.ReplyKeyboardMarkup(True, False)  # Creating button function
    user_kays.row('/login', '/cancel')  # creates 2 buttons in telegram
    answer = bot_t.send_message(message.from_user.id, text=constant.start_message, reply_markup=user_kays)  # Send message
    BotTLog().log_bot(answer.__dict__)
    messages_dict[message.message_id] = message.text  # Save users message to dict
    messages_dict[message.message_id + 1] = constant.start_message  # Save bot message to dict
    BotTLog().log_user(message)


@bot_t.message_handler(commands=['login'])  # Start login procedure
def handle_login(message):
    login_message = 'Please insert your login'  # login message
    hide_keys = telebot.types.ReplyKeyboardRemove()  # Hiding buttons
    answer = bot_t.send_message(message.from_user.id, text=login_message, reply_markup=hide_keys)  # Send message
    BotTLog().log_bot(answer.__dict__)
    # messages_dict[message.message_id] = message.text  # Save users message to dict
    # messages_dict[message.message_id + 1] = login_message  # Save bot answer
    global login_message_id
    login_message_id = message.message_id + 2  # Set login message id
    BotTLog().log_user(message)


@bot_t.message_handler(commands=['cancel'])  # Handle cancel function
def handle_cancel(message):
    hide_keys = telebot.types.ReplyKeyboardRemove()  # remove buttons function
    answer = bot_t.send_message(message.from_user.id, text='Canceled', reply_markup=hide_keys)  # remove buttons
    BotTLog().log_bot(answer.__dict__)
    BotTLog().log_user(message)


@bot_t.message_handler(content_types=['text'])  # main handler
def handle_text(message):
    messages_dict[message.message_id] = message.text  # Save users message to dict

    BotTLog().log_user(message)

    if len(message.text) > 250:
        message.text = message.text[:250]

    if log.find_one({'chat_id': message.chat.id}) is not None:
        previous_message = log.find_one({'chat_id': message.chat.id})['messages'].get(str(message.message_id - 1))
        if previous_message is not None:
            previous_message_text = previous_message['text']
        else:
            previous_message_text = 'No messages'
    else:
        previous_message_text = 'No messages'

    if 'Please insert your login' == previous_message_text:  # Ask for login
        response = 'Please insert your password'
        answer = bot_t.send_message(chat_id=message.chat.id, text=response)
        BotTLog().log_bot(answer.__dict__)
        global pass_message_id
        pass_message_id = message.message_id + 2
    elif previous_message_text == 'Please insert your password':  # Ask for password
        login = log.find_one({'chat_id': message.chat.id})['messages'].get(str(login_message_id))['text']
        password = log.find_one({'chat_id': message.chat.id})['messages'].get(str(pass_message_id))['text']

        billing = billing_api.Billingpy.billing_login(login, password)
        if type(billing) == str:
            answer = bot_t.send_message(chat_id=message.chat.id, text='Login or password incorrect.'
                                                                      ' Please try again\n        /login')
            BotTLog().log_bot(answer.__dict__)
        elif billing.get('name') is not None:
            response = 'Hello, ' + billing['name']
            answer = bot_t.send_message(chat_id=message.chat.id, text=response)
            BotTLog().log_bot(answer.__dict__)
            answer = bot_t.send_message(chat_id=message.chat.id, text='Please erase login and password for security')
            BotTLog().log_bot(answer.__dict__)
            if access.find_one({'chat_id': message.chat.id, 'access_lvl': 'user'}) is None:
                access.insert({'chat_id': message.chat.id, 'access_lvl': 'user', 'time': datetime.now(),
                               'bill': billing['bill']})
        else:
            answer = bot_t.send_message(chat_id=message.chat.id, text='Login or password incorrect'
                                                                      'Please try again\n           /login')
            BotTLog().log_bot(answer.__dict__)
    # Answering all other qestions using Dialog flow bot
    else:
        request = apiai.ApiAI(constant.token_dialog).text_request()  # token API for Dialogflow
        request.lang = 'en'  # На каком языке будет послан запрос
        request.session_id = 'Tech_bot_beta'  # ID Сессии диалога (нужно, чтобы потом учить бота)
        request.query = message.text  # Посылаем запрос к ИИ с сообщением от юзера
        print('user: ' + str(message.text) + '  ' + str(message.chat.id))
        responseJson = json.loads(request.getresponse().read().decode('utf-8'))
        response = responseJson['result']['fulfillment']['speech']  # Разбираем JSON и вытаскиваем ответ
        if response[:7] == 'Access1':  # If answer of AI need authentication or not
            if access.find_one({'chat_id': message.chat.id})['access_lvl'] == 'user':  # If he has it print message
                answer = bot_t.send_message(chat_id=message.chat.id, text=response[7:])
                BotTLog().log_bot(answer.__dict__)
            elif access.find_one({'chat_id': message.chat.id})['access_lvl'] == 'admin':  # If admin logged in
                response = 'Best admin ever'
                answer = bot_t.send_message(chat_id=message.chat.id, text=response)
                BotTLog().log_bot(answer.__dict__)
            else:  # If user han't logged in starts router_logging.py in prosses
                response = 'To get this information you need to log in'
                answer = bot_t.send_message(chat_id=message.chat.id, text=response)
                BotTLog().log_bot(answer.__dict__)
                handle_logging_in(message)
        elif response:  # usual answer sending
            answer = bot_t.send_message(chat_id=message.chat.id, text=response)
            BotTLog().log_bot(answer.__dict__)
            print('bott: ' + response)
        else:
            # if Dialog flow bot doesn't know what to answer he sends nothing
            if message.chat.id == 470147640:
                response = 'Go fuck yourself!'
                answer = bot_t.send_message(chat_id=message.chat.id, text=response)
                BotTLog().log_bot(answer.__dict__)
            else:
                response = "I can't understand"
                answer = bot_t.send_message(chat_id=message.chat.id, text=response)
                BotTLog().log_bot(answer.__dict__)


# noinspection PyBroadException
try:
    bot_t.polling(none_stop=True, interval=0)  # Replaces while cycle
# ConnectionError and ReadTimeout because of possible timeout of the requests library

except exceptions.ReadTimeout as ReedErr:
    bot_t.send_message(chat_id=445110178, text=ReedErr)
    bot_t.send_message(chat_id=445110178, text=datetime.now())
    run('python3 /home/alphanet/python/Bot/bot.py', shell=True)
    sleep(15)
except TypeError as TypeErr:
    bot_t.send_message(chat_id=445110178, text=TypeErr)
    bot_t.send_message(chat_id=445110178, text=datetime.now())
    run('python3 /home/alphanet/python/Bot/bot.py', shell=True)
    sleep(15)
except KeyError as keyerr:
    bot_t.send_message(chat_id=445110178, text=keyerr)
    bot_t.send_message(chat_id=445110178, text=datetime.now())
    sleep(10)
except:
    bot_t.send_message(chat_id=445110178, text='Какая-то херня')
    bot_t.send_message(chat_id=445110178, text=datetime.now())
    sleep(10)
    run('python3 /home/alphanet/python/Bot/bot.py', shell=True)
