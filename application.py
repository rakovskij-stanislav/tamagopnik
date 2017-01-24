# гитхаб создателя библиотеки - https://github.com/eternnoir/pyTelegramBotAPI
import telebot
from telebot import types
import extra # тут хранятся тексты
import db # тут хранятся пользователи
import _thread #задел на будущее
import random
import config # тут хранится логин-пароль от бота
import time

__author__ = "Rakovskij Stanislav"
__ver__    = "0.1"

### импортируем базу данных игроков
player_base = db.db()

### инициализация бота
bot = telebot.TeleBot(config.telebot)

# действия, которые надо применить при комманде start. Она может играть роль принудительного начала новой игры.
@bot.message_handler(commands=['start'])
def send_welcome(mes):
    #print(mes)
    if mes.chat.id in player_base.base.keys():
        #если старый игрок требует старт
        player_base.base[mes.chat.id].recovery=True
        markup = types.ReplyKeyboardMarkup()
        it_a = types.KeyboardButton('/new Начать новую игру')
        it_b = types.KeyboardButton('Продолжить прошлую игру')
        markup.row(it_a)
        markup.row(it_b)
        bot.send_message(mes.chat.id, "У тебя уже есть незавершенная игра, что будем делать?", reply_markup=markup)
    else:
        ###что делать, если игрок действительно новый
        player = db.player()
        player.last_motion = ['startroom', 'quest', 0]
        player_base.base.update({mes.chat.id:player})
        send_message(mes) #основная функция по обработке сообщений

@bot.message_handler(commands=['help'])
def send_help(mes):
    bot.send_message(mes.chat.id, 'Понимаю, тут должен быль хелп-гайд, но его нет пока')

@bot.message_handler(commands=['new'])
def new_start(mes): #служебная комманда для быстрого удаления информации о текущем пользователе
    if mes.chat.id in player_base.base:
        player_base.base.pop(mes.chat.id)
    send_message(mes)
    return ''


@bot.message_handler()
def send_message(mes):
    #Основная часть движка
    if mes.chat.id not in player_base.base: #хехе, если кто-то прошмыгнул мимо /start
        send_welcome(mes)
        return ''
    player = player_base.base[mes.chat.id]
    player.recovery = False
    player.turns += 1
    player.last_activity = time.time()
    #print("extra."+player.last_motion[0])
    local_room = eval("extra."+player.last_motion[0]+'()', {"player":player, "extra":extra}) #получаем информацию о комнате
    dialog = eval('local_room.' + player.last_motion[1])
    pos = player.last_motion[2]
    message = str(mes.text)
    #print('Info :', local_room, dialog, pos, mes)
    #print("Info2 :", str(type(dialog[pos])))
    #print("Info3 :", str(dialog[pos]))
    print('Info :', mes.chat.id, mes.text)
    if str(type(dialog[pos])) == "<class 'str'>": #для обычных текстов
        player.last_motion[2]+=1
        #player_base.base[mes.chat.id] = player
        sender(mes, text=dialog[pos])
        send_message(mes)
        return ''
    else:
        #need execute motions:
        motion = dialog[pos]
        if motion[0] == "choose":
            motto = motion[1]
            vars = motto.keys()
            text = '%Твой выбор:%'
            if message in vars: #если игрок прислал ответ
                #sender(mes, "ti molode4", markup)
                player.last_motion[2]=0
                player.last_motion[1] = motto[message]
                player_base.base[mes.chat.id] = player
                send_message(mes)
                return ''
            else: #если мы лишь перешли на этот блок или надо повторить отправку
                #sender(mes, "tebe otdam otvet", markup)
                if len(motion)==3:
                    text=motion[2]
                markup = types.ReplyKeyboardMarkup()
                for i in vars:
                    markup.row(types.KeyboardButton(i))
                #print("GTXFNFTV ^ твой выбор")
                bot.send_message(mes.chat.id, text, reply_markup=markup, parse_mode="html")
                #print("gs,jh отправлен")
                return ''

        elif motion[0] == "goto":
            player.last_motion[0] = motion[1]
            player.last_motion[1] = motion[2]
            player.last_motion[2] = 0
            player_base.base[mes.chat.id] = player
            send_message(mes)
            return ''

        elif motion[0] == "end":
            player_base.base.pop(mes.chat.id)
            bot.send_message(mes.chat.id, motion[1], parse_mode="html")
            return ''

        elif motion[0] == "take":
            player.inventory.append(motion[1])
            player.last_motion[2]+=1
            player_base.base[mes.chat.id] = player
            if len(motion)==3:
                bot.send_message(mes.chat.id, motion[2], parse_mode="html")
            send_message(mes)
            return ''

        elif motion[0] == "drop":
            if motion[1] not in player.inventory:
                bot.send_message(mes.chat.id, "Обнаружена нецелостность квеста. Сообщите об этом автору.\n Техническая информация :"+str(local_room)+'/'+str(dialog)+'/'+str(pos))
                print('ERROR 9',local_room, dialog, pos, mes)
                return ''
            del player.inventory[player.inventory.index(motion[1])]
            player.last_motion[2]+=1
            player_base.base[mes.chat.id] = player
            if len(motion)==3:
                bot.send_message(mes.chat.id, motion[2], parse_mode="html")
            else:
                bot.send_message(mes.chat.id, "#_#", parse_mode="html")
            send_message(mes)
            return ''

        elif motion[0] == "item_exist":
            if motion[1] in player.inventory:
                player.last_motion[1] = motion[2]
                player.last_motion[2] = 0
            else:
                player.last_motion[1] = motion[3]
                player.last_motion[2] = 0
            send_message(mes)
            return ''

        elif motion[0] == "random":
            ran = len(motion)-1
            ans = random.randrange(ran)
            player.last_motion[1] = motion[1+ans]
            player.last_motion[2] = 0
            send_message(mes)
            return ''
        elif motion[0] == "compile":
            ans = motion[1]
            ans = eval('"'+ans+'".format('+motion[2]+')')
            player.last_motion[2]+=1
            bot.send_message(mes.chat.id, ans, parse_mode="html")
            send_message(mes)
            return ""

        bot.send_message(mes.chat.id, 'Еще надо подумать', parse_mode="html")

def sender(mes, text):
    bot.send_message(mes.chat.id, text, parse_mode="html")

"""
@bot.message_handler(commands=['start', 'help'])
def send_welcome(mes):
    markup = types.ReplyKeyboardMarkup()
    itembtna = types.KeyboardButton('a')
    itembtnv = types.KeyboardButton('v')
    itembtnc = types.KeyboardButton('c')
    itembtnd = types.KeyboardButton('d')
    itembtne = types.KeyboardButton('e')
    markup.row(itembtna, itembtnv)
    markup.row(itembtnc, itembtnd, itembtne)
    bot.send_message(mes.chat.id, "Choose one letter:", reply_markup=markup)

@bot.message_handler()
def send(mes):
    markup = types.ReplyKeyboardHide(selective=False)
    bot.send_message(mes.chat.id, mes.text, reply_markup=markup)
"""

bot_thread = _thread.start_new(bot.polling, ())
a = input("meh, it is an exit")
###
