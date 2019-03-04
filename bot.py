# -*- coding: utf-8 -*-

import config
import db
import telebot
import os
import io
from telebot import types
from PIL import Image

#Использовать прокси. Если сервер бота в стране без блокировок. Закомментировать две строчки ниже
#from telebot import apihelper
#apihelper.proxy = config.proxy

bot = telebot.TeleBot(config.token)

#Подключаемся к базе, создаем/проверяем наличие таблицы
c = db.db()
c.createtable()

modes = {
    1: 'Square tiles + Left',
    2: 'Rectangles 4x5 + Left',
    3: 'Square tiles + Middle',
    4: 'Rectangles 4x5 + Middle',
    5: 'Square tiles + Right',
    6: 'Rectangles 4x5 + Right'
}

def get_coord_set(w, h, cid):
    areas = []
    mode = c.step(cid)
    if mode%2 and w < 2 * h or not mode%2 and 5 * w < 8 * h:
        bot.send_message(cid, "Picture is not wide enough. I can not even cut it into two parts.\nSend another one.")
    elif mode%2:
        num = 1
        while w >= num * h:
            areas.append(((num - 1) * h, 0, num * h, h))
            num += 1
    else:
        num = 1
        while w >= num * h * 4 // 5:
            areas.append(((num - 1) * h * 4 // 5, 0, num * h * 4 // 5, h))
            num += 1
    return areas

def mode_first_set():
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(text='Square tiles', callback_data='-1')
    button1 = telebot.types.InlineKeyboardButton(text='Rectangles 4x5', callback_data='-2')
    markup.add(button)
    markup.add(button1)
    return markup

def mode_second_set(mode):
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(text='Left', callback_data=str(mode))
    button1 = telebot.types.InlineKeyboardButton(text='Middle', callback_data=str(mode+2))
    button2 = telebot.types.InlineKeyboardButton(text='Right', callback_data=str(mode+4))
    markup.add(button)
    markup.add(button1)
    markup.add(button2)
    return markup

@bot.message_handler(commands=['mode'])
def start(m):
    cid = m.chat.id
    bot.send_message(chat_id = cid, text='Choose cutting mode:', reply_markup = mode_first_set())

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.message:
        cid = call.message.chat.id
        mid = call.message.message_id
        if call.data == '-1':
            bot.edit_message_text(chat_id=cid, message_id=mid, text="Mode changed to Square tiles. Choose how to align a set of cut photos:", reply_markup = mode_second_set(1))
        elif call.data == '-2':
            bot.edit_message_text(chat_id=cid, message_id=mid, text="Mode changed to Rectangles 4x5. Choose how to align a set of cut photos:", reply_markup = mode_second_set(2))
        elif int(call.data) > 0:
            c.insert(call.message.chat, int(call.data))
            bot.edit_message_text(chat_id=cid, message_id=mid, text="Mode changed to " + modes[int(call.data)] + ".\nSend me a picture as a 'File'.")

@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    if not c.exist(cid):  # if user hasn't used the "/start" command yet:
        bot.send_message(cid, "Hello, stranger, let me scan you...")
        c.insert(m.chat, 1)
        bot.send_message(cid, "Scanning complete, now I know you.")
        command_help(m)
    else:
        bot.send_message(cid, "I already know you, no need for me to scan you again!\nUse /help to find out how to use the bot.") 

@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "InstaSplit bot will easy split up your panorama into multiple square tiles or pieces 4x5 for post those photos to Instagram as part of a single post. Use /mode to change cutting mode.\n\nSend me a photo as a 'File' to process."
    bot.send_message(cid, help_text)  # send the generated help page

@bot.message_handler(content_types=['document'])
def handle_document(m):
    if m.document.mime_type.startswith('image/'):
        try:
            cid = m.chat.id
            bot.send_chat_action(cid, 'upload_photo')#'upload_photo','typing'
            file_info = bot.get_file(m.document.file_id)
            download = bot.download_file(file_info.file_path)
            img = Image.open(io.BytesIO(download))
            frmt = img.format
            w, h = img.size
            areas = get_coord_set(w, h, cid)
            for area in areas:
                imcrop = img.crop(area)
                bio = io.BytesIO()
                bio.name = m.document.file_name
                imcrop.save(bio, format=frmt, subsampling=0, quality=100)
                bio.seek(0)
                bot.send_document(cid, bio)
        except (e):
            bot.send_message(m.chat.id, 'Unknown error. Try again.')
    else:
        bot.send_message(m.chat.id, 'Please send static panoramic image file.')

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    bot.send_message(m.chat.id, 'Please send me a picture as a File, not as a Photo.')

@bot.message_handler(content_types=["text"])
def repeat_all_messages(m):
    bot.send_message(m.chat.id, 'Use /help to find out how to use the bot.')

bot.polling()