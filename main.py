#!/usr/bin/python
# -*- coding: UTF-8 -*-
#Requres python
import os
import subprocess
import sys
import serial
import psutil
import time
import smtplib
import ConfigParser
import urllib
import logging

# Начало описания класса UPS_BT
class UPS_BT:
    vin=0
    vout=0
    vbat=0
    cur=0
    tpri=0
    tsec=0
    curin=0
    pwr=0
    apwr=0
    allmode=0
    frq=0
    port=''

    # Список состояний инвертера
    state_description = {
	23: 'Режим работы от сети. Зарядка АКБ',
	27: 'Режим работы от сети. Поддержание заряда АКБ',
	25: 'Режим работы от сети. АКБ заряжена',
	35: 'Режим работы от АКБ. Заряд 100%',
	37: 'Режим работы от АКБ. Заряд 75% ',
	57: 'Режим работы от АКБ. Низкий заряд АКБ'
    }

    # Описания команд инвертера для печати
    parameter_description={
        'vin':'Напряжение входящей сети, В',
	'curin':'Сила тока входящей сети, А',
        'vout':'Напряжение выходящей сети, В',
	'vbat':'Напряжение батареи, В',
        'cur':'Сила тока АКБ, A',
        'tpri':'Температура перв. чаcти, Град',
        'tsec':'Температура втор. чаcти, Град',
        'pwr':'Полная мощность нагрузки, KVA',
        'apwr':'Активная мощность нагрузки, KVA',
        'allmode':'Режим работы инвертера',
        'frq':'Частота входящей сети, ГЦ'
    }

    def __init__(self, port):
	self.port=port

    # Функция отправляет команду ИБП и возвращает результат выполнения
    def ExecUPSCommand(self, ups, ucommand):
        ups.write('?'+ucommand+'\r')
        res=ups.readline()

        return res
    
    # Функция получает текущие параметры от ИБП
    def GetDataFromUPS(self):
        ser = serial.Serial(self.port)
	cmd_list=['vin','curin','vout','vbat','cur','tpri','tsec','pwr','apwr','allmode','frq']
	for cmd in cmd_list:
            res = self.ExecUPSCommand(ser, cmd)
    	    param = res.split('=')
	    param_name = ''.join(param[0])
	    if param_name == 'allmode':
		param_value = int(''.join(param[1]).replace(',', '.'))
	    else:
		param_value = float(''.join(param[1]).replace(',', '.'))
	    self.__dict__[param_name] = param_value
        ser.close()             # close port

    # Функция возвращает описание текущих параметров ИБП для печати или отправки на почту
    def GetCurrentStateForPrint(self):
	res = ''
	for key in self.parameter_description:
	    res+=''+ self.parameter_description[key]+': '+str(self.__dict__[key])+'\r\n'

	res = self.state_description.setdefault(self.allmode, 'Состояние не определено. Сообщите разработчику')+'\r\n'+res
	return res

# Конец описания класса UPS

def CheckUPSConnection():     # Check start BT connection
    btConnectionActive = False
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['cmdline', 'pid'])
        except psutil.NoSuchProcess:
            pass
        else:
	    cmd = ''.join(pinfo['cmdline'])
	    if cmd.find('rfcommconnect') > -1:
		btConnectionActive = True
		print "BT Connection already estabilished: "
		print(pinfo)
    if btConnectionActive == False:
        print "Starting BT connection"
        child = os.path.join(os.path.dirname(__file__), "./connectbt.py")
        command = [sys.executable, child]
        pipe = subprocess.Popen(command, stdin=subprocess.PIPE)
        pipe.stdin.close()
        time.sleep(10)
    
def SendEmail(MailText, Send, MailServer, MailPort, Login, Password, Mailto, Subject):	# Sens Email notification
    if Send != True:
	    return
    print "Sending mail..."
    smtpObj = smtplib.SMTP(MailServer, MailPort)
    smtpObj.starttls()
    smtpObj.login(Login,Password)
    BODY = "From: "+Login+"\r\nTo: "+ Mailto+"\r\nSubject: "+Subject+"\r\n\r\n"+MailText
    smtpObj.sendmail(Login,Mailto, BODY)
    smtpObj.quit()

def SendSMS(Send, Server, User, Password, Phone, Text):
    if Send != True:
	return
    print "Sending SMS..."
    response = urllib.urlopen('http://'+Server+'/sendsms?username='+User+'&password='+Password+'&phonenumber='+Phone+'&message='+Text)
    print(response.read())

def SendTelegram(Send, Server, ChatID, Text):
    if Send != True:
	return
    print "Sending Telegram message..."
    message = urllib.urlencode({'chat_id':ChatID,'text':Text})
    response = urllib.urlopen(Server, message)
    print(response.read())

def ShutdownPC():
    cmd = 'sudo shutdown -P now'	#Linux
#    cmd = 'shutdown -s'	#Windows
#    p = subprocess.Popen(cmd, shell=True)

# MAIN PROGRAM
if __name__ == '__main__':

# Получим настройки программы
    file_config = os.path.join(os.path.dirname(__file__), "./ups.conf")
    file_log = os.path.join(os.path.dirname(__file__), "./ups_log.txt")
    conf = ConfigParser.RawConfigParser()
    conf.read(file_config)
    ups_port = conf.get("ups", "port")
    ups_btaddr = conf.get("ups", "btaddr")
    ups_laststate = conf.getfloat("ups", "laststate")
    ups_vpoweroff = conf.getfloat("ups", "vpoweroff")
    mail_send =  conf.getboolean("mail", "send")
    mail_login =  conf.get("mail", "login")
    mail_server =  conf.get("mail", "mailserver")
    mail_port =  conf.get("mail", "mailport")
    mail_passw =  conf.get("mail", "password")
    mail_to = conf.get("mail", "mailto")
    sms_send =  conf.getboolean("sms", "send")
    sms_login =  conf.get("sms", "login")
    sms_server =  conf.get("sms", "server")
    sms_passw =  conf.get("sms", "password")
    sms_to = conf.get("sms", "smsto")
    telegram_send = conf.getboolean("telegram", "send")
    telegram_server = conf.get("telegram", "server")
    telegram_chatid = conf.get("telegram", "chatid")

    logging.basicConfig(filename=file_log,level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    for i in range(0,5):
# Подключение к ИБП
        ups = UPS_BT(ups_port)
	CheckUPSConnection()
# Получение данных от ИБП
        ups.GetDataFromUPS()
	StatePreview = ups.GetCurrentStateForPrint()
        print StatePreview
	if (StatePreview!=''):
	    break;

# ПРОВЕРКА РЕЖИМОВ РАБОТЫ ИБП
    fpoweroff = False		# Если установлен флаг, то сервер будет выключен
    message = ''		# Сообщение для логов и отправки на почту. К данному сообщению будет добавлено описание текущего состояния ИБП
    theme="UPS: Отключение рабочего сервера" # Тема письма и текст СМС сообщения

# 1. Проверка режима работы от АКБ. Критический заряд
    
    if ups.allmode == 57:
	message = 'Critical battery State. Shutdown PC'
	fpoweroff=True

# 2. Проверка: напряжение батареи достигло порогового
    if ups.vbat <= ups_vpoweroff:
	message = 'Low Battery Voltage. Shutdown PC'
	fpoweroff=True

# 3.  Проверка изменения состояния инвертера
    if ups_laststate != ups.allmode:
#	message = 'Changing state: Last state: '+str(ups_laststate)+' Current state: '+str(ups.allmode)
	message = 'Изменение режима работы ИБП с "'+ups.state_description.setdefault(ups_laststate, 'Состояние не определено. Сообщите разработчику')+'" (Код: '+str(ups_laststate)+') на '+ups.state_description.setdefault(ups.allmode, 'Состояние не определено. Сообщите разработчику')+' (Код: '+str(ups.allmode)+')'
	theme = "UPS: Изменение режима работы инвертера"
	# Запишем текущий режим работы инвертера в настройках
        conf.set("ups", "laststate", ups.allmode)
        with open(file_config, "w") as config:
            conf.write(config)

#    logging.debug('UPS status: '+str(ups.allmode))
    if message=='': 	# Если сообщение об ошибке не заполнено, то все ОK
	exit(0)

# Если сообщение заполнено, то запишем его в логи и отправим письмо
    logging.debug(message + '\r\n' + StatePreview)
    SendEmail(message + '\r\n' + StatePreview, mail_send, mail_server, mail_port, mail_login, mail_passw, mail_to, theme)
    SendTelegram(telegram_send, telegram_server, telegram_chatid, 'EA.UPS: '+message)

# Отключение серевера при необходимости
    if fpoweroff == True:
	SendSMS(sms_send, sms_server, sms_login, sms_passw, sms_to, theme)
	ShutdownPC()
	exit(0)