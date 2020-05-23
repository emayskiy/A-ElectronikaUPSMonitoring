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
    vlo_off = 0
    vlo_start = 0
    vlo_warn=0
    slp=0
    offline=0
    vout=0
    vch=0
    ich=0
    vfl=0
    ifl=0
    pwr_slp=0
    snd=0
    podk=0
    vline_lo=0
    vline_hi=0
    frq_lo=0
    frq_hi=0
    fast=0
    eco=0
    veco_lo=0
    sell=0
    veco_hi=0
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

    # Описания параметров инвертера для печати
    parameter_description={
        'vin':'Напряжение входящей сети, В',
	'curin':'Сила тока входящей сети, А',
        'vout':'Напряжение выходящей сети, В',
	'vbat':'Напряжение батареи, В',
        'cur':'Сила тока АКБ, В',
        'tpri':'Температура перв. чаcти, Град',
        'tsec':'Температура втор. чаcти, Град',
        'pwr':'Полная мощность нагрузки, KVA',
        'apwr':'Активная мощность нагрузки, KVA',
        'allmode':'Режим работы инвертера',
        'frq':'Частота входящей сети, ГЦ'
    }

    # Описания команд инвертера для печати
    command_description={
	'vlo_off': 'Напряжение отключения, В',
	'vlo_start': 'Напряжение переподключения, В',
	'vlo_warn': 'Напряжение предупреждения, В',
	'slp': 'Разрешение спящего режима',
	'offline': 'Разрешение переключения на сеть',
	'vout': 'Выходное напряжение, В',
	'vch': 'Напряжение заряда, В',
	'ich': 'Ток заряда, А',
	'vfl': 'Напряжение поддерживающей стадии заряда, В',
	'ifl': 'Ток переключения на поддерживающую стадию заряда, А',
	'pwr_slp': 'Мощность нагрузки для выхода из спящего режима, KVA',
	'snd': 'Разрешение звуковой индикации',
	'podk': 'Разрешение гибридного режима',
	'vline_lo': 'Минимальное напряжение сети, В',
	'vline_hi': 'Максимальное напряжение сети, В',
	'frq_lo': 'Минимальная частота сети, Гц',
	'frq_hi': 'Максимальная частота сети, Гц',
	'fast' : 'Контроль формы сетевого напряжения',
	'sell': 'Разрешение продажи энергии в сеть',
	'eco': 'Разрешение приоритетного использования аккумулятора',
	'veco_lo': 'Напряжение заряда АКБ, при котором происходит отключение от сети и переход на работу от аккумулятора, В',
	'veco_hi': 'Напряжение разряда АКБ, при котором происходит переключение на сеть, В'
    }

    def __init__(self, port):
	self.port=port

    # Функция отправляет команду ИБП и возвращает результат выполнения
    def ExecUPSCommand(self, ups, ucommand):
        ups.write('?'+ucommand+'\r')
        res=ups.readline()

        return res
    
    # Функция отправляет команду ИБП и возвращает результат выполнения
    def ExecUPSCommandProg(self, ucommand, uvalue):
	cmd = ucommand+'='+uvalue
	print "Sending command ("+cmd+") to ups..."
        ser = serial.Serial(self.port)
        ser.write(cmd+'\r')
        res=ser.readline()
        print 'Результат выполнения команды: '+ res
	
        return res
    
    # Функция получает текущие параметры от ИБП
    def GetDataFromUPS(self):
	print "Getting extended data from UPS..."
        ser = serial.Serial(self.port)
	cmd_list=['vin','curin','vout','vbat','cur','tpri','tsec','pwr','apwr','allmode','frq', 'vlo_off', 'vlo_start', 'vlo_warn', 'slp', 'offline', 'vout', 'vch', 'ich', 'vfl', 'ifl', 'pwr_slp', 'snd', 'podk', 'vline_lo', 'vline_hi', 'frq_lo', 'frq_hi', 'fast', 'sell', 'eco', 'veco_lo', 'veco_hi']
	for cmd in cmd_list:
            res = self.ExecUPSCommand(ser, cmd)
    	    param = res.split('=')
	    param_name = ''.join(param[0])
	    param_value = ''.join(param[1]).replace(',', '.')
#	    if param_name == 'allmode':
#		param_value = int(''.join(param[1]).replace(',', '.'))
#	    else:
#		param_value = float(''.join(param[1]).replace(',', '.'))
	    self.__dict__[param_name] = param_value
        ser.close()             # close port

    # Функция возвращает описание текущих параметров ИБП для печати или отправки на почту
    def GetCurrentStateForPrint(self):
	res = '\r\n************************* Текущее состояние ИБП ******************************* \r\n\r\n'
	res += self.state_description.setdefault(int(self.allmode), 'Состояние не определено. Сообщите разработчику')+'\r\n\r\n'
	for key in self.parameter_description:
	    res+=''+ self.parameter_description[key]+' ('+key+')'+': '+str(self.__dict__[key])+''

	res += '\r\n******************* Текущие значения параметров ИБП ************************** \r\n\r\n'
	for key in self.command_description:
	    res+=''+ self.command_description[key]+' ('+key+')'+': '+str(self.__dict__[key])+''

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
    # У меня для отправки используется GSM-шлюз OpenVox. Заменить URL на любой СМС-сервис
    response = urllib.urlopen('http://'+Server+'/sendsms?username='+User+'&password='+Password+'&phonenumber='+Phone+'&message='+Text)
    print(response.read())

def ShutdownPC():
    cmd = 'sudo shutdown -P now'	#Linux
    #cmd = 'shutdown -s'	#Windows
#    p = subprocess.Popen(cmd, shell=True)
#    p.wait()

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

    logging.basicConfig(filename=file_log,level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Подключение к ИБП
    ups = UPS_BT(ups_port)
    CheckUPSConnection()

# Получение данных от ИБП
    ups.GetDataFromUPS()

    print ups.GetCurrentStateForPrint()

    prog_name = raw_input('Введите имя параметра для изменения значения (Указано в скобках для каждого параметра): ')
    if ups.command_description.has_key(prog_name)==False:
	print 'Неверное имя параметра: '+prog_name
	exit(0)
    prog_descr = ups.command_description[prog_name]
    prog_current = ups.__dict__[prog_name]
    print 'Параметр: '+prog_descr+' ('+prog_name+') Текущее значение: '+prog_current
    
    prog_value = raw_input('Введите новое значение параметра '+prog_descr+': ')
    print 'Внимание: внимательно проверьте значение параметра. Если не уверены, то не подтверждайте изменение'
    prog_agree = raw_input('Изменить значение параметра '+prog_descr+' с '+prog_current+' на '+prog_value+'? Введите Y/y для подтверждения...')
    if prog_agree.upper() != 'Y':
	print 'Отказ от изменения параметра'
	exit(0)

    res = ups.ExecUPSCommandProg(prog_name, prog_value)