
# -*- coding: utf-8 -*-
import os, sys, threading, time
from modules import cbpi, app
from modules.core.hardware import SensorActive
from modules.core.props import Property
from bluepy import btle
import struct
import threading

PeripheralConnection = object()
PeripheralAddrName = ""
 
lock = threading.Lock()
 
def GetPeripheralConnection(address):
    global PeripheralConnection
    global PeripheralAddrName
    
    lock.acquire()

    if not PeripheralAddrName:
        print "connecting...."
        PeripheralAddrName = address
        try:
            print "PeripheralAddrName=%s" % (PeripheralAddrName)
            PeripheralConnection = btle.Peripheral(address)
            print "PeripheralConnection=%s" % (str(PeripheralConnection))
        except:
            print "Couldn't connect"
    
    lock.release()
    
@cbpi.sensor
class ArduinoBLE_Temperature(SensorActive):

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, default_value="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, default_value="run blelisten.py: '1101....'")
    CharTemp = Property.Text("Characteristic Temperature", configurable=True, default_value="run blelisten.py '2204...'")

    def get_unit(self):
        '''
        :return: Unit of the sensor as string. Should not be longer than 3 characters
        '''
        return "°C" if self.get_config_parameter("unit", "C") == "C" else "°F"

    def stop(self):
        '''
        Stop the sensor. Is called when the sensor config is updated or the sensor is deleted
        :return: 
        '''
        pass

    def execute(self):
        '''
        Active sensor has to handle its own loop
        :return: 
        '''
        global PeripheralConnection
        GetPeripheralConnection(self.PeripheralAddress)
        self.Peripheral = PeripheralConnection

        print "temp.Peripheral = ", self.Peripheral
        while self.is_running():

            self.sleep(5)
            ch = self.Peripheral.getCharacteristics()
            temp = 0
            
            for c in ch:

                if str(c.uuid) == self.CharTemp:          
                    if c.supportsRead():
                        s1 = c.read()
                        temp = struct.unpack("<HH", s1)[0] /100.0
                        if (self.get_unit() == "C"):
                            self.data_received(temp)
                        else:
                            self.data_received(9.0 / 5.0 * temp + 32.0)
                    
                    self.sleep(5)

    @classmethod
    def init_global(cls):
        '''
        Called one at the startup for all sensors
        :return: 
        '''

@cbpi.sensor
class ArduinoBLE_Excel_Xaxis(SensorActive):

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, default_value="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, default_value="run blelisten.py: '1101....'")
    CharExcel_X = Property.Text("Characteristic Excel_X", configurable=True, default_value="run blelisten.py '2201...'")

    def stop(self):
        '''
        Stop the sensor. Is called when the sensor config is updated or the sensor is deleted
        :return: 
        '''
        pass

    def execute(self):
        '''
        Active sensor has to handle its own loop
        :return: 
        '''
        global PeripheralConnection
        GetPeripheralConnection(self.PeripheralAddress)
        self.Peripheral = PeripheralConnection

        print "X.Peripheral = ", self.Peripheral
        while self.is_running():

            self.sleep(5)
            ch = self.Peripheral.getCharacteristics()
            temp = 0
            
            for c in ch:
                 if str(c.uuid) == self.CharExcel_X:
                    if c.supportsRead():
                        s1 = c.read()
                        excelX = struct.unpack("<HH", s1)[0]
                        self.data_received(excelX)
                    
                    self.sleep(5)
                    break

    @classmethod
    def init_global(cls):
        '''
        Called one at the startup for all sensors
        :return: 
        '''

@cbpi.sensor
class ArduinoBLE_Humidity(SensorActive):

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, default_value="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, default_value="run blelisten.py: '1101....'")
    CharHum = Property.Text("Characteristic Humidity", configurable=True, default_value="run blelisten.py '2205...'")

    def stop(self):
        '''
        Stop the sensor. Is called when the sensor config is updated or the sensor is deleted
        :return: 
        '''
        pass

    def execute(self):
        '''
        Active sensor has to handle its own loop
        :return: 
        '''
        global PeripheralConnection
        GetPeripheralConnection(self.PeripheralAddress)
        self.Peripheral = PeripheralConnection

        print "hum.Peripheral = ", self.Peripheral
        while self.is_running():

            self.sleep(5)
            ch = self.Peripheral.getCharacteristics()
            temp = 0
            
            for c in ch:
                if str(c.uuid) == self.CharHum:
                    if c.supportsRead():
                        s1 = c.read()
                        hum = struct.unpack("<HH", s1)[0] /100.0
                        self.data_received(hum)
                    
                    self.sleep(5)

    @classmethod
    def init_global(cls):
        '''
        Called one at the startup for all sensors
        :return: 
        '''

@cbpi.sensor
class ArduinoBLE_Pressure(SensorActive):

    PeripheralAddress = Property.Text("Peripheral Address", configurable=True, default_value="run blelisten.py for address")
    ServiceAddress = Property.Text("Service Address", configurable=True, default_value="run blelisten.py: '1101....'")
    CharPress = Property.Text("Characteristic Pressure", configurable=True, default_value="run blelisten.py '2206...'")

    def stop(self):
        '''
        Stop the sensor. Is called when the sensor config is updated or the sensor is deleted
        :return: 
        '''
        pass

    def execute(self):
        '''
        Active sensor has to handle its own loop
        :return: 
        '''
        global PeripheralConnection
        GetPeripheralConnection(self.PeripheralAddress)
        self.Peripheral = PeripheralConnection

        print "press.Peripheral = ", self.Peripheral
        while self.is_running():

            self.sleep(5)
            ch = self.Peripheral.getCharacteristics()
            temp = 0
            
            for c in ch:
                #print(str(c.uuid))

                if str(c.uuid) == self.CharPress:
                    if c.supportsRead():
                        s1 = c.read()
                        pressure = struct.unpack("<HH", s1)[0] /100.0
                        self.data_received(pressure)
                    
                    self.sleep(5)

    @classmethod
    def init_global(cls):
        '''
        Called one at the startup for all sensors
        :return: 
        '''