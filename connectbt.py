#!/usr/bin/python
# -*- coding: UTF-8 -*-
#Requres python

import subprocess
import ConfigParser

def ConnectBT(BTAddr):
    print 'Try to connecting: '+BTAddr
    p = subprocess.Popen(['rfcomm', 'bind', '0'], stdout=subprocess.PIPE)
    p = subprocess.Popen(['rfcomm', 'release', '0', BTAddr], stdout=subprocess.PIPE)
    p = subprocess.Popen(['rfcomm', 'connect', '0', BTAddr], stdout=subprocess.PIPE)

# MAIN PROGRAM
if __name__ == '__main__':

    conf = ConfigParser.RawConfigParser()
    conf.read("ups.conf")
    btaddr= conf.get("ups", "btaddr")

    ConnectBT(btaddr)
