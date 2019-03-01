# -*- coding: utf-8 -*-

import config
import telebot
#from telebot import apihelper

#apihelper.proxy = config.proxy

bot = telebot.TeleBot(config.token)

knownUsers = []
userStep = {}

commands = {
    'start'       : 'Познакомиться с ботом',
    'help'        : 'Получить информацию о доступных командах',
}

def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        return 0

@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet:
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
        bot.send_message(cid, "Привет, рад знакомству!")
        command_help(m)
    else:
        bot.send_message(cid, "О! Привет! А я тебя уже знаю!")

@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "Сейчас доступны вот такие команды: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе
    bot.send_message(message.chat.id, "Вы написали: " + message.text)

bot.polling()