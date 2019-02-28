# -*- coding: utf-8 -*-

token = '617409655:AAE_rwH6q7VHvmuyU8swt7ekFTvZ8XJUeLI'
proxy = {'https':'socks5://telegram:autopassword@auto.socks5.ss5.ch:1090'}

#You can use proxy for request. apihelper.proxy object will use by call requests proxies argument.
#
#from telebot import apihelper
#
#apihelper.proxy = {'http':'http://10.10.1.10:3128'}
#If you want to use socket5 proxy you need install dependency pip install requests[socks] and make sure, that you have the latest version of gunicorn, PySocks, pyTelegramBotAPI, requests and urllib3.
#
#apihelper.proxy = {'https':'socks5://userproxy:password@proxy_address:port'}