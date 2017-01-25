# гитхаб создателя библиотеки - https://github.com/eternnoir/pyTelegramBotAPI
import telebot
from telebot import types
import extra  # тут хранятся тексты
import db  # тут хранятся пользователи
import _thread  # задел на будущее
import random
import config  # тут хранится логин-пароль от бота
import time
from datetime import datetime

__author__ = "Rakovskij Stanislav"
__ver__ = "0.1"
admin_id = 287004218

# импортируем базу данных игроков
player_base = db.db()

# инициализация бота
bot = telebot.TeleBot(config.telebot[0])


@bot.message_handler(commands=['admin'])
def admin_panel(mes):
    if mes.chat.id != admin_id:
        return ''
    com = str(mes.text).split()
    if len(com) > 1:
        if com[1] in ['load', 'merge', 'save', 'wipe', "online"]:
            if com[1] == 'load':
                player_base.load()
            if com[1] == 'merge':
                player_base.merge()
            if com[1] == 'save':
                player_base.save()
            if com[1] == 'wipe':
                player_base.wipe()
            if com[1] == "online":
                i = 0
                t = time.time()
                for q in player_base.base.keys():
                    if t - player_base.base[q].last_activity < 60 * 5:
                        i += 1
                bot.send_message(mes.chat.id, "Online users : " + str(i))


# действия, которые надо применить при комманде start. Она может играть роль принудительного начала новой игры.
@bot.message_handler(commands=['start'])
def send_welcome(mes):
    # print(mes)
    if mes.chat.id in player_base.base.keys():
        # если старый игрок требует старт
        player_base.base[mes.chat.id].recovery = True
        markup = types.ReplyKeyboardMarkup()
        it_a = types.KeyboardButton('/new Начать новую игру')
        it_b = types.KeyboardButton('/con Продолжить прошлую игру')
        markup.row(it_a)
        markup.row(it_b)
        bot.send_message(mes.chat.id, "У тебя уже есть незавершенная игра, что будем делать?", reply_markup=markup)
    else:
        ###что делать, если игрок действительно новый
        player = db.player()
        player.last_motion = ['startroom', 'quest', 0]
        player_base.base.update({mes.chat.id: player})
        send_message(mes)  # основная функция по обработке сообщений


@bot.message_handler(commands=['help'])
def send_help(mes):
    bot.send_message(mes.chat.id, 'Понимаю, тут должен быль хелп-гайд, но его нет пока')


@bot.message_handler(commands=['new'])
def new_start(mes):  # служебная комманда для быстрого удаления информации о текущем пользователе
    if mes.chat.id in player_base.base:
        player_base.base.pop(mes.chat.id)
    print("InfoNEW :", mes.chat.id)
    send_message(mes)
    return ''


@bot.message_handler(commands=['con'])
def new_cont(mes):  # продолжить игру. надо снять флаг ожидания выбора
    if mes.chat.id not in player_base.base:  # хехе, если кто-то прошмыгнул мимо /start
        send_welcome(mes)
        return ''
    print("InfoCON :", mes.chat.id)
    player = player_base.base[mes.chat.id]
    player.waiting_answer = False
    send_message(mes)
    return ''


@bot.message_handler()
def send_message(mes):
    # Основная часть движка
    if mes.chat.id not in player_base.base:  # хехе, если кто-то прошмыгнул мимо /start
        send_welcome(mes)
        return ''
    player = player_base.base[mes.chat.id]
    player.recovery = False
    player.turns += 1
    player.last_activity = time.time()
    # print("extra."+player.last_motion[0])
    local_room = eval("extra." + player.last_motion[0] + '()',
                      {"player": player, "extra": extra})  # получаем информацию о комнате
    dialog = eval('local_room.' + player.last_motion[1])
    pos = player.last_motion[2]
    message = str(mes.text)
    # print('Info :', local_room, dialog, pos, mes)
    # print("Info2 :", str(type(dialog[pos])))
    # print("Info3 :", str(dialog[pos]))
    # print('Info :', mes.chat.id, mes.text)
    if str(type(dialog[pos])) == "<class 'str'>":  # для обычных текстов
        player.last_motion[2] += 1
        # player_base.base[mes.chat.id] = player
        print('Info0 :', mes.chat.id, 'Прошлое сообщение человека :', mes.text, '\n   Отвечаю ему', dialog[pos])
        bot.send_message(mes.chat.id, dialog[pos], parse_mode="html")
        send_message(mes)
        return ''
    else:
        # need execute motions:
        motion = dialog[pos]
        if motion[0] == "choose":
            motto = motion[1]
            varss = motto.keys()
            text = '%Твой выбор:%'
            if message in varss:  # если игрок прислал ответ
                # sender(mes, "ti molode4", markup)
                player.last_motion[2] = 0
                player.last_motion[1] = motto[message]
                player.waiting_answer = False
                send_message(mes)
                return ''
            else:  # если мы лишь перешли на этот блок или надо повторить отправку
                # sender(mes, "tebe otdam otvet", markup)
                if len(motion) == 3:
                    text = motion[2]
                markup = types.ReplyKeyboardMarkup()
                for i in varss:
                    markup.row(types.KeyboardButton(i))
                print('Info1 :', mes.chat.id, "return a choose", str(motion[1]))
                if player.waiting_answer == False:
                    player.waiting_answer = True
                    bot.send_message(mes.chat.id, text, reply_markup=markup, parse_mode="html")

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
            print('Info2 :', mes.chat.id, mes.text)
            bot.send_message(mes.chat.id, motion[1], parse_mode="html")
            return ''

        elif motion[0] == "take":
            player.inventory.append(motion[1])
            player.last_motion[2] += 1
            player_base.base[mes.chat.id] = player
            if len(motion) == 3:
                print('Info3 :', mes.chat.id, mes.text)
                bot.send_message(mes.chat.id, motion[2], parse_mode="html")
            send_message(mes)
            return ''

        elif motion[0] == "drop":
            if motion[1] not in player.inventory:
                print('Info4 :', mes.chat.id, mes.text)
                bot.send_message(mes.chat.id,
                                 "Обнаружена нецелостность квеста. Сообщите об этом автору.\n Техническая информация :" + str(
                                     local_room) + '/' + str(dialog) + '/' + str(pos))
                print('ERROR 9', mes.chat.id, local_room, dialog, pos, mes)
                return ''
            del player.inventory[player.inventory.index(motion[1])]
            player.last_motion[2] += 1
            player_base.base[mes.chat.id] = player
            if len(motion) == 3:
                print('Info5 :', mes.chat.id, mes.text)
                bot.send_message(mes.chat.id, motion[2], parse_mode="html")
            else:
                print('Info6 :', mes.chat.id, mes.text)
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
            ran = len(motion) - 1
            ans = random.randrange(ran)
            player.last_motion[1] = motion[1 + ans]
            player.last_motion[2] = 0
            send_message(mes)
            return ''
        elif motion[0] == "compile":
            ans = motion[1]
            ans = eval('"' + ans + '".format(' + motion[2] + ')')
            player.last_motion[2] += 1
            print('Info7 :', mes.chat.id, mes.text)
            bot.send_message(mes.chat.id, ans, parse_mode="html")
            send_message(mes)
            return ""

        elif motion[0] == "reset_but":
            player.last_motion[2] += 1
            print('Info8 :', mes.chat.id, mes.text)
            markup = types.ReplyKeyboardHide(selective=False)
            bot.send_message(mes.chat.id, motion[1], parse_mode="html", reply_markup=markup)
            send_message(mes)
            return ''

        bot.send_message(mes.chat.id, 'Еще надо подумать', parse_mode="html")


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


def metrika():
    # Тому, кто всё-таки отважился читать мой код
    # Я тут подумал, можно в Гугл.Формах хранить логи. Но законно ли это? Я же почти раз в минуту пишу логи, не забанят ли за ~1440 обращений с одного ip?
    # Пожалуйста, ответьте, интересно ведь
    name = str(datetime.now())[:-7]
    with open('metrika/'+name + '.csv', "w") as f:
        f.write(name + ';0\n')
    time.sleep(60)
    while True:
        with open('metrika/'+name + '.csv', "a") as f:
            t = time.time()
            i = 0
            for player in player_base.base.keys():
                if player_base.base[player].last_activity - t < 60 * 5:
                    i += 1
            f.write(str(datetime.now())[:-7] + ';' + str(i) + '\n')
        print("#Logged")
        time.sleep(60)


# Единственная метрика на данный момент - онлайн, сохранять буду в формате csv
metr = input("Введите '1', если хотите сохранять метрику : ")
if metr == "1":
    now = datetime.now()
    metr_thread = _thread.start_new(metrika, ())

bot.polling()
