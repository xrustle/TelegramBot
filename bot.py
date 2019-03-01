# -*- coding: utf-8 -*-

import config
import telebot
#import logging
#from telebot import apihelper

#apihelper.proxy = config.proxy

#logger = telebot.logger
#telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

bot = telebot.TeleBot(config.token)

commands = {  # command description used in the "help" command
	'start'       : 'Get used to the bot',
	'help'        : 'Gives you information about the available commands',
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, """Мой тестовый бот, развернутый на Heroku""")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, """Бот на все сообщения отвечает зеркально. Больше он ничего не умеет:(""")

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе
    bot.send_message(message.chat.id, "Вы написали: " + message.text)

if __name__ == '__main__':
    bot.polling(none_stop=True)