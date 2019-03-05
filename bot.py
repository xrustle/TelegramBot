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
    1: 'Square tiles + Left', #[ i*i for i in range(1,10)]
    2: 'Rectangles 4x5 + Left',
    3: 'Square tiles + Middle',
    4: 'Rectangles 4x5 + Middle',
    5: 'Square tiles + Right',
    6: 'Rectangles 4x5 + Right'
}

def get_coord_set(w, h, cid):
    mode = c.step(cid)
    areas = []
    if mode%2 and w < 2 * h or not mode%2 and 5 * w < 8 * h:
        bot.send_message(cid, 'Picture is not wide enough. I can not even cut it into two parts.')
    else:
        k2 = (mode-1)%3 #0 for Left, 1 for Middle, 2 for Right
        step = h + (mode%2 -1) * h // 5 #При mode%2 = 0 сдвигаем на пятую высоты. Шаг будет 4/5
        x0 = k2 * (w % step) // 2 #Координата x - начало старта
        n = 1 #номер плитки слева направо
        while w >= n * step:
            areas.append((x0 + (n - 1) * step, 0, x0 + n * step, h))
            n += 1
        areas.insert(0, n-1)
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
            bot.edit_message_text(chat_id=cid, message_id=mid, text='Mode changed to Square tiles. Choose how to align a set of cut photos:', reply_markup = mode_second_set(1))
        elif call.data == '-2':
            bot.edit_message_text(chat_id=cid, message_id=mid, text='Mode changed to Rectangles 4x5. Choose how to align a set of cut photos:', reply_markup = mode_second_set(2))
        elif int(call.data) > 0:
            c.insert(call.message.chat, int(call.data))
            bot.edit_message_text(chat_id=cid, message_id=mid, text='Mode changed to ' + modes[int(call.data)] + ".\nSend me a picture as a 'File'.")

@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    if not c.exist(cid):  # if user hasn't used the "/start" command yet:
        bot.send_message(cid, 'Hello, stranger, let me scan you...')
        bot.send_chat_action(cid, 'typing')
        c.insert(m.chat, 1)
        bot.send_message(cid, 'Scanning complete, I know you now.')
        command_help(m)
    else:
        bot.send_message(cid, 'I already know you, no need for me to scan you again!\nUse /help to find out how to use the bot.') 

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
            bot.send_chat_action(cid, 'typing')
            file_info = bot.get_file(m.document.file_id)
            download = bot.download_file(file_info.file_path)
            img = Image.open(io.BytesIO(download))
            frmt = img.format
            w, h = img.size
            if not c.exist(cid):
                c.insert(m.chat, 1)
            areas = get_coord_set(w, h, cid)
            num = areas.pop(0)
            if num > 1:
                bot.send_message(cid, 'Ok, now I will send '+str(num)+' parts of your photo.')
            for area in areas:
                bot.send_chat_action(cid, 'upload_photo')
                imcrop = img.crop(area)
                bio = io.BytesIO()
                bio.name = m.document.file_name
                imcrop.save(bio, format=frmt, subsampling=0, quality=100)
                bio.seek(0)
                bot.send_document(cid, bio)
            if num > 1:
                bot.send_message(cid, "That's it!\nSend another photo or try to change /mode.")
        except (e):
            bot.send_message(cid, 'Unknown error:( Try again or text me. @batorov')
    else:
        bot.send_message(cid, 'Please send static panoramic image file.')

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    bot.send_message(m.chat.id, 'Please send me a picture as a File, not as a Photo.')

@bot.message_handler(content_types=["text"])
def repeat_all_messages(m):
    bot.send_message(m.chat.id, 'Use /help to find out how to use the bot.')

bot.polling()