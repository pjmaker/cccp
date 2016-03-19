#! /usr/bin/env python2
'''
cccp.py - a simple test harness for the SMA Cluster Controller, whence
    cccp (cluster controller controller program). The SMA Cluster Controller
    provides a MODBUS-TCP interface which controls and monitors a group
    of SMA inverters. 

INSTALL: this program uses the twisted framework and pymodbus both of
   which can be installed by pip install.
'''

from pymodbus.constants import Defaults
from pymodbus.client.sync import ModbusTcpClient
from twisted.internet import reactor, protocol
from twisted.internet.task import LoopingCall
 
# from control import * -- unused for now

'''Maximum PV output for this cluster which must be set by hand'''
PvMaxP = 50.0 # change this as appropriate

'''Current PV output in kW'''
PvP = 0
'''Current PV active power setpoint in kW'''
PvSetP = 0
'''Current PV reactive power setpoint in kW'''
PvSetQ = 0

def writer():
    '''write the setpoints'''
    global client
    global PvSetP, PvSetQ, PvP, PvQ, PvMaxP

    # vary the setpoints
    PvSetP = (PvSetP + 10) % PvMaxP
    PvSetP = limit(PvSetP, 1, 100)
    PvSetQ = 0 

    PvSetPRaw = 10000.0*(PvSetP/PvMaxP)
    PvSetQRaw = 10000.0*(PvSetQ/PvMaxP)

    rr = client.write_registers(40022,
                                [PvSetQRaw,PvSetPRaw],
                                unit=2)

def reader():
    '''read the current status'''
    global client
    global PvP, PvSetP

    rr = client.read_input_registers(30775,2,unit=1)
    print "PvP= ", ((rr.registers[0]<<16) | rr.registers[1])/1000.0,
    print " ~ ", PvSetP
    

# make the connection
client = ModbusTcpClient('172.16.200.41', 502)
client.connect()

# 
loopwriter = LoopingCall(f=writer)
loopreader = LoopingCall(f=reader)
loopwriter.start(10, now=False) 
loopreader.start(1, now=False)

reactor.run()
