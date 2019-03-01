# -*- coding: utf-8 -*-

import config
import telebot
#import logging
#from telebot import apihelper

#apihelper.proxy = config.proxy

#logger = telebot.logger
#telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

bot = telebot.TeleBot(config.token)

knownUsers = []  # todo: save these in a file,
userStep = {}  # so they won't reset every time the bot restarts

commands = {  # command description used in the "help" command
	'start'       : 'Get used to the bot',
	'help'        : 'Gives you information about the available commands',
}

def get_user_step(uid):
if uid in userStep:
return userStep[uid]
else:
        knownUsers.append(uid)
        userStep[uid] = 0
print("New user detected, who hasn't used \"/start\" yet")
return 0

@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
if cid not in knownUsers:  # if user hasn't used the "/start" command yet:
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
        bot.send_message(cid, "Hello, stranger, let me scan you...")
        bot.send_message(cid, "Scanning complete, I know you now")
        command_help(m)  # show the new user the help page
else:
        bot.send_message(cid, "I already know you, no need for me to scan you again!")

@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "The following commands are available: \n"
for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе
    bot.send_message(message.chat.id, "Вы написали: " + message.text)

bot.send_chat_action(cid, 'typing')
bot.polling()